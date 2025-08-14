import logging

import numpy

from newclid.api import GeometricSolver, GeometricSolverBuilder
from newclid.heuristics._index import HeuristicName
from newclid.heuristics._interface import Heuristic, HeuristicSetup
from newclid.heuristics.angle_vertices import (
    AngleVerticesHeuristicConfig,
)
from newclid.heuristics.centers_of_cyclic import (
    CentersOfCyclicHeuristicConfig,
)
from newclid.heuristics.geometric_objects import (
    read_geometric_objects_from_predicate_constructions,
)
from newclid.heuristics.heuristic_from_config import (
    HeuristicConfig,
    heuristic_from_config,
)
from newclid.heuristics.line_intersections import LineIntersectionsHeuristicConfig
from newclid.jgex.constructions import ALL_JGEX_CONSTRUCTIONS
from newclid.jgex.definition import JGEXDefinition
from newclid.jgex.errors import JGEXConstructionError
from newclid.jgex.formulation import JGEXFormulation
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.jgex.to_newclid import JGEXClauseConsequences, add_clause_to_problem
from newclid.predicate_types import PredicateArgument
from newclid.problem import ProblemSetup, predicate_to_construction

defs = JGEXDefinition.to_dict(ALL_JGEX_CONSTRUCTIONS)
LOGGER = logging.getLogger(__name__)
rng = numpy.random.default_rng(42)


def apply_complete_the_picture_heuristics(
    problem_setup: ProblemSetup,
    jgex_problem: JGEXFormulation,
    rng: numpy.random.Generator,
    max_new_points: int | None = None,
) -> tuple[
    ProblemSetup, JGEXFormulation, dict[HeuristicName, list[JGEXClauseConsequences]]
]:
    """Apply the "complete the picture" heuristics to the given JGEX problem."""
    complete_the_picture_heuristics_configs: list[HeuristicConfig] = [
        CentersOfCyclicHeuristicConfig(),
        LineIntersectionsHeuristicConfig(),
        AngleVerticesHeuristicConfig(),
    ]
    new_problem = problem_setup.model_copy(deep=True)
    new_points: set[PredicateArgument] = set()
    max_new_points = max_new_points or 50
    clauses_per_heuristic: dict[HeuristicName, list[JGEXClauseConsequences]] = {}
    for heuristic_config in complete_the_picture_heuristics_configs:
        heuristic = heuristic_from_config(heuristic_config)
        problem_setup, added_clauses_consequences = apply_heuristics_on_nc_problem(
            problem_setup=problem_setup,
            jgex_problem=jgex_problem,
            heuristic=heuristic,
            rng=rng,
            max_new_points=max_new_points - len(new_points),
        )
        new_problem = problem_setup
        clauses_per_heuristic[heuristic_config.heuristic_name] = (
            added_clauses_consequences
        )
        for clause_consequences in added_clauses_consequences:
            new_points.update(clause_consequences.new_points.keys())

    return new_problem, jgex_problem, clauses_per_heuristic


def apply_heuristics_on_nc_problem(
    problem_setup: ProblemSetup,
    jgex_problem: JGEXFormulation,
    heuristic: Heuristic,
    rng: numpy.random.Generator,
    max_new_points: int | None = None,
) -> tuple[ProblemSetup, list[JGEXClauseConsequences]]:
    goal_less_problem = problem_setup.model_copy(deep=True)
    goal_less_problem.goals = tuple()  # Force saturation
    solver: GeometricSolver = GeometricSolverBuilder(rng=rng).build(goal_less_problem)
    solver.run()

    newclid_problem = problem_setup.model_copy()
    predicate_constructions_deduced = [
        predicate_to_construction(predicate)
        for predicate in solver.proof_state.graph.hyper_graph.keys()
    ]

    goals = problem_setup.goals
    relevant_predicates_constructions = (
        set(goals)
        .union(newclid_problem.assumptions)
        .union(predicate_constructions_deduced)
    )
    points: list[PredicateArgument] = [p.name for p in newclid_problem.points]
    lines, circles, angles, free_points = (
        read_geometric_objects_from_predicate_constructions(
            jgex_problem, relevant_predicates_constructions
        )
    )

    heuristic_setup = HeuristicSetup(
        points=tuple(points),
        free_points=tuple(free_points),
        lines=tuple(lines),
        circles=tuple(circles),
        angles=tuple(angles),
        goals=goals,
    )

    max_new_points = max_new_points or 50
    added_points: set[PredicateArgument] = set()
    new_clauses = heuristic.new_clauses(heuristic_setup, max_new_points, rng)
    successful_clauses_consequences: list[JGEXClauseConsequences] = []
    for clause in new_clauses:
        try:
            newclid_problem, clause_consequences = add_clause_to_problem(
                newclid_problem, clause, defs, rng, 1
            )
        except JGEXConstructionError as e:
            LOGGER.warning(f"Failed to add clause {clause}: {e}")
            continue
        except ValueError as e:
            LOGGER.warning(
                f"Failed to add clause due to a validation error for clause {clause}: {e}"
            )
            continue

        added_points.update(clause_consequences.new_points.keys())
        successful_clauses_consequences.append(clause_consequences)

    return newclid_problem, successful_clauses_consequences


def build_nc_problem_from_jgex_problem(
    jgex_problem: JGEXFormulation,
    rng: numpy.random.Generator,
) -> ProblemSetup:
    goal_less_problem = jgex_problem.model_copy(deep=True)
    jgex_problem_setup = (
        JGEXProblemBuilder(rng=rng).with_problem(goal_less_problem).build()
    )
    solver: GeometricSolver = GeometricSolverBuilder(rng=rng).build(jgex_problem_setup)
    return solver.proof_state.problem


if __name__ == "__main__":
    problem_txt = (
        "a b = segment a b; c = midpoint c a b; d = eqdistance d a a b, eqdistance d b a b;"
        " o = midpoint o c d; e = on_dia e c d; f = on_circum f c d e, eqdistance f e c d"
        " ? coll f o e"
    )
    jgex_problem = JGEXFormulation.from_text(problem_txt)
    nc_problem = build_nc_problem_from_jgex_problem(jgex_problem, rng)
    new_problem, _resulting_jgex_problem, _clauses_consequences_per_heuristic = (
        apply_complete_the_picture_heuristics(
            nc_problem, jgex_problem, rng, max_new_points=20
        )
    )
    new_solver = GeometricSolverBuilder().build(new_problem)

    new_success = new_solver.run()
    print(new_solver.run_infos)
