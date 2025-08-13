import logging
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Iterable, Iterator

import numpy as np
from newclid.api import GeometricSolver, GeometricSolverBuilder
from newclid.jgex.clause import JGEXClause, JGEXConstruction
from newclid.jgex.constructions import ALL_JGEX_CONSTRUCTIONS
from newclid.jgex.definition import JGEXDefinition
from newclid.jgex.errors import JGEXConstructionError
from newclid.jgex.formulation import ALPHABET, JGEXFormulation, alphabetize
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.jgex.to_newclid import JGEXClauseConsequences, add_clause_to_problem
from newclid.predicate_types import PredicateArgument
from newclid.problem import ProblemSetup
from newclid.proof_state import ProofBuildError
from numpy.random import Generator as RngGenerator
from pydantic import BaseModel, Field

from ncdgen.constructions import ConstructionDefinition
from ncdgen.generation_configuration import (
    DiagramGenerationConfig,
    IntersectCases,
    SweepSelection,
)
from ncdgen.sampling import (
    combinations_in_random_order,
    sample_from_pmf,
    sample_order_from_pmf,
)

LOGGER = logging.getLogger(__name__)


class SubproblemSummaryStats(BaseModel):
    """This is the metadata about the SUBPROBLEM generation."""

    skipped_not_enough_rules_applications_subproblems: int = 0
    """ How many times we skipped to get a subproblem because it was too short. """
    unhandled_failure_to_build_subproblem_count: int = 0
    """ How many times we failed to get a subproblem because of an unhandled exception. """
    skipped_blacklisted_aux_setup_pairs: int = 0
    """ How many times we skipped a subproblem because aux setup pair was a false positive on a previous goal. """


class FailedClauseAttempt(BaseModel):
    problem: ProblemSetup
    """ The problem we were trying to add the clause to. """
    clause: JGEXClause
    """ The clause we were trying to add. """
    attempt_time: float
    """ How long did it take to check whether we can add it? """


class DiagramGenerationMetadata(BaseModel):
    """This is the metadata about the DIAGRAM generation. NOT about the individual datapoints."""

    run_uuid: str
    diagram_uuid: str
    is_predefined_diagram: bool
    """ Whether the problem was specified as an input, which means
    we do NOT generate anything. """

    config: DiagramGenerationConfig
    """ The config we used to generate this diagram. """

    diagram_construction_time_sec: float
    """ How long we spent trying to get a diagram. """

    diagram_succeeded: bool
    """ If we didn't manage to get a diagram, we can still store the metadata for counters. """

    saturation_succeeded: bool = False
    """ Whether saturation was successful. """

    saturation_time_sec: float | None = None
    """ How long we spent trying to saturate the diagram. Assumes we succeeded in getting a diagram.
    If diagram_succeeded is False, this will be None. """

    agent_saturation_stats: BaseModel | None = None
    """ Agent statistics during the saturation process. """

    failed_clause_attempts: list[FailedClauseAttempt] = []
    """ List of all the failed clause attempts on that diagram generation process. """

    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    subproblem_summary_stats: SubproblemSummaryStats = Field(
        default_factory=SubproblemSummaryStats
    )


SetupGraph = dict[str, set[str]]


@dataclass
class Diagram:
    """Represents a geometric diagram with its associated data.

    Attributes:
        solver: The solver with everything in it to solve the diagram
        problem: The geometric problem associated with the diagram
        dependencies: List of dependencies in the diagram
        setup_graph: Dictionary mapping points to their dependencies
    """

    solver: GeometricSolver
    jgex_problem: JGEXFormulation
    nc_problem: ProblemSetup
    setup_graph: SetupGraph
    jgex_clauses_consequences: dict[JGEXClause, JGEXClauseConsequences]


def build_diagram(
    cfg: DiagramGenerationConfig,
    sweep_cfg: SweepSelection,
    free: dict[str, ConstructionDefinition],
    intersect: dict[str, ConstructionDefinition],
    other: dict[str, ConstructionDefinition],
    rng: RngGenerator,
) -> tuple[Diagram | None, DiagramGenerationMetadata]:
    """Builds a geometric diagram by incrementally adding constructions.

    The algorithm works as follows:
    1. If debug_problem is provided, builds that specific problem and returns
    2. Otherwise, builds a diagram incrementally:
        a. Starts with a random base construction from FREE (e.g. triangle, circle)
        b. Adds sampled number of additional free points based on config
        c. Repeatedly adds new constructions until reaching desired point count:
            - Tries to add either OTHER constructions (parallel lines, circles etc.)
              or INTERSECT constructions (1 or 2 intersection points)
            - For each construction type, makes multiple attempts with different
              random input points
            - If no valid construction is found after all attempts, returns None
            - Otherwise adds the successful construction and continues

    Args:
        cfg: Configuration controlling diagram generation parameters
            - min_pts/max_pts: Desired point count range
            - attempts_per_construction: Number of random attempts per construction
            - debug_problem: Optional specific problem to build instead
            - Various sampling parameters for construction choices

    Returns:
        Built Diagram object if successful, None if construction fails
    """

    if cfg.debug_problem is not None:
        p = JGEXFormulation.from_text(cfg.debug_problem)
        diagram = _attempt_diagram_build(clauses=p.clauses, cfg=cfg)
        metadata = DiagramGenerationMetadata(
            run_uuid=cfg.run_uuid,
            diagram_uuid=str(uuid.uuid4()),
            config=cfg,
            is_predefined_diagram=True,
            diagram_construction_time_sec=0.0,
            diagram_succeeded=True,
        )
        return diagram, metadata

    if cfg.initial_jgex_problem is not None:
        jgex_problem, _ = alphabetize(
            JGEXFormulation.from_text(cfg.initial_jgex_problem)
        )
        jgex_problem.goals = ()

    else:
        n_additional_free = sample_from_pmf(
            cfg.pmf_additional_free_points_sweep[
                sweep_cfg.additional_free_points_sweep_selection
            ],
            rng=rng,
        )
        jgex_problem = _random_initial_base_jgex_problem(
            rng=rng,
            free=free,
            n_additional_free=n_additional_free,
        )

    jgex_problem.auxiliary_clauses = ()  # Remove auxiliary clauses if any
    jgex_problem_builder = JGEXProblemBuilder(
        rng=rng, max_attempts_per_clause=10
    ).with_problem(jgex_problem)
    nc_problem = jgex_problem_builder.build()
    clauses_consequences = jgex_problem_builder.clauses_consequences

    metadata = DiagramGenerationMetadata(
        run_uuid=cfg.run_uuid,
        diagram_uuid=str(uuid.uuid4()),
        config=cfg,
        is_predefined_diagram=True,
        diagram_construction_time_sec=0.0,
        diagram_succeeded=False,
        saturation_time_sec=None,
    )

    added_num_points = rng.integers(cfg.min_pts, cfg.max_pts + 1)  # type: ignore
    added_pts = 0
    start_time = time.perf_counter()

    while added_pts < added_num_points:
        new_clause_result = _add_potential_clauses_to_nc_problem(
            nc_problem=nc_problem,
            cfg=cfg,
            sweep_cfg=sweep_cfg,
            intersect=intersect,
            other=other,
            metadata=metadata,
            rng=rng,
        )
        if new_clause_result is not None:
            new_nc_problem, new_clause, new_clause_consequences = new_clause_result
            jgex_problem.setup_clauses += (new_clause,)
            clauses_consequences[new_clause] = new_clause_consequences
            LOGGER.debug(f"Successfully added clause: {new_clause}")
            added_pts += len(new_clause.points)
            nc_problem = new_nc_problem
        else:
            metadata.diagram_succeeded = False
            metadata.diagram_construction_time_sec = time.perf_counter() - start_time
            return None, metadata

    try:
        solver = GeometricSolverBuilder(rng=rng).build(nc_problem)
    except ProofBuildError:
        return None, metadata

    metadata.diagram_succeeded = True
    metadata.diagram_construction_time_sec = time.perf_counter() - start_time
    diagram = Diagram(
        solver=solver,
        nc_problem=nc_problem,
        jgex_problem=jgex_problem,
        jgex_clauses_consequences=clauses_consequences,
        setup_graph=setupgraph(jgex_problem),
    )
    return diagram, metadata


DEFS_DICT = JGEXDefinition.to_dict(ALL_JGEX_CONSTRUCTIONS)


def _add_potential_clauses_to_nc_problem(
    nc_problem: ProblemSetup,
    cfg: DiagramGenerationConfig,
    sweep_cfg: SweepSelection,
    intersect: dict[str, ConstructionDefinition],
    other: dict[str, ConstructionDefinition],
    metadata: DiagramGenerationMetadata,
    rng: RngGenerator,
) -> tuple[ProblemSetup, JGEXClause, JGEXClauseConsequences] | None:
    existing_pts = tuple(pt.name for pt in nc_problem.points)
    for potential_clause in _potential_clauses(
        existing_pts=existing_pts,
        cfg=cfg,
        sweep_cfg=sweep_cfg,
        INTERSECT=intersect,
        OTHER=other,
        rng=rng,
    ):
        start_time = time.perf_counter()
        try:
            new_nc_problem, new_clause_consequences = add_clause_to_problem(
                problem=nc_problem,
                clause=potential_clause,
                defs=DEFS_DICT,
                rng=rng,
                max_attempts=cfg.attempts_per_clause,
            )
        except JGEXConstructionError:
            LOGGER.debug(f"Failed to add clause: {potential_clause}")
            attempt_time = time.perf_counter() - start_time
            failed_clause_attempt = FailedClauseAttempt(
                problem=nc_problem,
                clause=potential_clause,
                attempt_time=attempt_time,
            )
            metadata.failed_clause_attempts.append(failed_clause_attempt)
            continue
        return new_nc_problem, potential_clause, new_clause_consequences
    LOGGER.debug("Failed to add any potential clauses.")
    return None


def _random_initial_base_jgex_problem(
    rng: RngGenerator, free: dict[str, ConstructionDefinition], n_additional_free: int
) -> JGEXFormulation:
    """Builds a random base construction from the free constructions."""
    name, con = rng.choice(list(free.items()))  # type: ignore
    assert isinstance(con, ConstructionDefinition)
    assert isinstance(name, str)

    pts: tuple[PredicateArgument, ...] = tuple(
        PredicateArgument(p) for p in ALPHABET[: con.in_args]
    )
    base_constr = JGEXClause(
        points=pts,
        constructions=(JGEXConstruction.from_name_and_args(name=name, args=pts),),
    )
    clauses = [base_constr]

    LOGGER.debug(f"Base construction: {name} {pts}")

    for _ in range(n_additional_free):
        name = "free"
        pt_name = PredicateArgument(ALPHABET[len(pts)])
        clauses.append(
            JGEXClause(
                points=(pt_name,),
                constructions=(
                    JGEXConstruction.from_name_and_args(name="free", args=(pt_name,)),
                ),
            )
        )
        pts += (pt_name,)

    return JGEXFormulation(
        name=f"random_base_construction_with_{n_additional_free}_free_points",
        setup_clauses=tuple(clauses),
        goals=(),
    )


def _potential_clauses(
    existing_pts: tuple[PredicateArgument, ...],
    cfg: DiagramGenerationConfig,
    sweep_cfg: SweepSelection,
    INTERSECT: dict[str, ConstructionDefinition],
    OTHER: dict[str, ConstructionDefinition],
    rng: RngGenerator,
) -> Iterator[JGEXClause]:
    """Attempts to add a new construction to an existing geometric diagram.

    This function tries to add either intersection points or other geometric constructions
    (like parallel lines, circles etc.) to an existing diagram. The order and type of
    constructions to try is sampled based on configuration parameters.

    For intersection constructions:
    - Samples how many intersection points to try to add at once (e.g. 1 or 2)
    - For each count, tries different combinations of intersection constructions
      (e.g. line-line, line-circle intersections)
    - Makes multiple random attempts with different input points for each construction

    For other constructions:
    - Tries constructions like parallel lines, circles, squares etc.
    - For each construction type, makes multiple attempts with different random input points
    - Special handling for parallelograms and squares to order construction arguments correctly

    Args:
        existing_pts: List of points already in the diagram
        existing_clauses: List of existing construction clauses
        cfg: Configuration controlling construction parameters

    Returns:
        If successful, returns a new clause to add to the diagram.
        If no valid construction found, returns None

    Raises:
        AssertionError: If input points aren't valid or config parameters missing
    """
    assert all(pt in ALPHABET for pt in existing_pts)
    remaining_pts = tuple(
        PredicateArgument(pt) for pt in ALPHABET if pt not in existing_pts
    )

    # Sample whether to try intersection or other constructions first
    construction_group_order = sample_order_from_pmf(
        cfg.pmf_intersect_vs_other_sweep[sweep_cfg.intersect_vs_other_sweep_selection],
        rng,
    )

    for group in construction_group_order:
        if len(remaining_pts) < 1:
            break
        match group:
            case IntersectCases.INTERSECT:
                intersection_counts = sample_order_from_pmf(
                    cfg.pmf_num_intersecting_to_sample_sweep[
                        sweep_cfg.num_intersecting_to_sample_sweep_selection
                    ],
                    rng,
                )
                yield from _sample_intersect_constructions(
                    existing_pts=existing_pts,
                    intersection_counts=intersection_counts,
                    attempts_per_clause=cfg.attempts_per_clause,
                    remaining_pts=remaining_pts,
                    INTERSECT=INTERSECT,
                    rng=rng,
                )
            case IntersectCases.OTHER:
                yield from _sample_other_constructions(
                    existing_pts=existing_pts,
                    remaining_pts=remaining_pts,
                    attempts_per_construction=cfg.attempts_per_clause,
                    OTHER=OTHER,
                    rng=rng,
                )


def _sample_intersect_constructions(
    existing_pts: tuple[PredicateArgument, ...],
    remaining_pts: tuple[PredicateArgument, ...],
    intersection_counts: list[int],
    attempts_per_clause: int,
    INTERSECT: dict[str, ConstructionDefinition],
    rng: RngGenerator,
) -> Iterator[JGEXClause]:
    # Get list of intersection constructions we can build with existing points
    applicable_intersection_constructions = [
        k for k, v in INTERSECT.items() if v.n_required_points <= len(existing_pts)
    ]

    # Try different counts of intersection points
    for n_intersections in intersection_counts:
        output_pt = remaining_pts[0]

        # Try different combinations of intersection constructions
        for chunk_construction_names in combinations_in_random_order(
            applicable_intersection_constructions, n_intersections, rng
        ):
            chunk_construction_specs = [
                INTERSECT[name] for name in chunk_construction_names
            ]

            LOGGER.debug(
                f"Attempting to add {IntersectCases.INTERSECT.value} {n_intersections} {chunk_construction_names}"
            )

            # Make multiple attempts with different random input points
            for _attempt_idx in range(attempts_per_clause):
                chunk_constructions: list[JGEXConstruction] = []
                for construction_name, construction_spec in zip(
                    chunk_construction_names, chunk_construction_specs
                ):
                    pts: list[PredicateArgument] = list(
                        rng.choice(
                            existing_pts,
                            size=construction_spec.n_required_points,
                            replace=False,
                        )
                    )

                    chunk_constructions.append(
                        JGEXConstruction.from_name_and_args(
                            name=construction_name, args=(output_pt, *pts)
                        )
                    )

                new_clause = JGEXClause(
                    points=(output_pt,),
                    constructions=tuple(chunk_constructions),
                )
                yield new_clause


def _sample_other_constructions(
    existing_pts: tuple[PredicateArgument, ...],
    remaining_pts: tuple[PredicateArgument, ...],
    attempts_per_construction: int,
    OTHER: dict[str, ConstructionDefinition],
    rng: RngGenerator,
) -> Iterator[JGEXClause]:
    # Get list of other constructions we can build with existing points
    buildable_other = [
        k for k, v in OTHER.items() if v.n_required_points <= len(existing_pts)
    ]
    pmf_other_constructions = {k: 1.0 / len(buildable_other) for k in buildable_other}
    other_construction_names = sample_order_from_pmf(pmf_other_constructions, rng)

    # Try each other construction type
    for construction_name in other_construction_names:
        spec = OTHER[construction_name]
        output_pts = list(remaining_pts[: spec.out_args])

        # Make multiple attempts with different random input points
        for _attempt_idx in range(attempts_per_construction):
            input_pts: list[PredicateArgument] = list(
                rng.choice(existing_pts, spec.n_required_points, replace=False)
            )
            construction_args: list[PredicateArgument] = output_pts + input_pts
            new_clause = JGEXClause(
                points=tuple(output_pts),
                constructions=(
                    JGEXConstruction.from_name_and_args(
                        name=construction_name, args=tuple(construction_args)
                    ),
                ),
            )
            yield new_clause


def _attempt_diagram_build(
    clauses: Iterable[JGEXClause],
    cfg: DiagramGenerationConfig,
) -> Diagram | None:
    problem = JGEXFormulation(setup_clauses=tuple(clauses), goals=())
    rng = np.random.default_rng(cfg.random_seed)
    try:
        problem_builder = JGEXProblemBuilder(rng=rng).with_problem(problem)
        problem_setup = problem_builder.build(
            max_attempts_to_satisfy_goals_numerically=cfg.attempts_per_diagram_build
        )
        solver = GeometricSolverBuilder(rng=rng).build(problem_setup)
    except (JGEXConstructionError, ProofBuildError):
        return None

    return Diagram(
        solver=solver,
        jgex_problem=problem,
        nc_problem=solver.proof_state.problem,
        jgex_clauses_consequences=problem_builder.clauses_consequences,
        setup_graph=setupgraph(problem),
    )


def setupgraph(prob: JGEXFormulation | str) -> SetupGraph:
    """Build a dependency graph showing how each point depends on other points.

    For each point in the problem, tracks which other points were needed to construct it.
    The dependencies are transitive - if point C depends on B which depends on A, then
    C will also show a dependency on A.

    Args:
        prob (ProblemJGEX | str): The geometric problem to analyze, either as a ProblemJGEX object
            or as a string that can be parsed into one.

    Returns:
        SetupGraph: A dictionary mapping each point name to the set of point names it
            depends on. The value set for a point includes both direct dependencies
            (points used in its construction) and indirect dependencies (points needed
            to construct its direct dependencies).

    Raises:
        AssertionError: If a point appears multiple times in the problem clauses.
    """
    if isinstance(prob, str):
        prob = JGEXFormulation.from_text(prob)
    points: dict[str, set[str]] = {}
    for clause in prob.clauses:
        for output_pt in clause.points:
            if output_pt in points:
                raise ValueError(
                    f"Point {output_pt} appears multiple times in the problem clauses."
                )
            points[output_pt] = set()
            for construction in clause.constructions:
                args = construction.args
                points[output_pt].update(args)
                for a in args:
                    points[output_pt].update(points.get(a, set()))
    return points
