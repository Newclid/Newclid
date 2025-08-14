from __future__ import annotations

import logging

from numpy.random import Generator as RngGenerator
from pydantic import BaseModel

from newclid.jgex.clause import JGEXClause, JGEXConstruction, is_numerical_argument
from newclid.jgex.definition import (
    JGEXDefinition,
    JGEXVariableName,
    SketchCall,
    mapping_from_construction,
)
from newclid.jgex.distances import (
    ensure_not_too_close_numerical,
    ensure_not_too_far_numerical,
)
from newclid.jgex.errors import JGEXConstructionError
from newclid.jgex.formulation import JGEXFormulation
from newclid.jgex.geometries import JGEXGeometry, JGEXPoint, reduce_intersection
from newclid.jgex.sketch import sketch
from newclid.numerical.geometries import PointNum
from newclid.predicate_types import PredicateArgument
from newclid.predicates import NUMERICAL_PREDICATES
from newclid.predicates._index import PredicateType
from newclid.problem import (
    PredicateConstruction,
    ProblemSetup,
    rename_predicate_construction,
)
from newclid.symbols.points_registry import Point
from newclid.tools import atomize

LOGGER = logging.getLogger(__name__)


def build_newclid_problem(
    problem: JGEXFormulation,
    defs: dict[str, JGEXDefinition],
    rng: RngGenerator,
    max_attempts_per_clause: int,
    include_auxiliary_clauses: bool,
) -> tuple[ProblemSetup, dict[JGEXClause, JGEXClauseConsequences]]:
    """Build a JGEX problem by finding coordinates for the points given the clauses constraints."""
    LOGGER.debug(f"Building JGEX problem '{problem.name}': {problem}")

    nc_problem = ProblemSetup(
        name=problem.name,
        points=(),
        assumptions=(),
        goals=(),
    )
    clauses_consequences: dict[JGEXClause, JGEXClauseConsequences] = {}

    clauses = problem.clauses if include_auxiliary_clauses else problem.setup_clauses
    for clause in clauses:
        nc_problem, clause_consequences = add_clause_to_problem(
            problem=nc_problem,
            clause=clause,
            defs=defs,
            rng=rng,
            max_attempts=max_attempts_per_clause,
        )
        clauses_consequences[clause] = clause_consequences

    nc_problem = nc_problem.with_new(new_goals=problem.goals)
    return nc_problem, clauses_consequences


def add_clause_to_problem(
    problem: ProblemSetup,
    clause: JGEXClause,
    defs: dict[str, JGEXDefinition],
    rng: RngGenerator,
    max_attempts: int,
) -> tuple[ProblemSetup, JGEXClauseConsequences]:
    """Add a clause to a problem, returning the new problem and the consequences of the clause.

    Raises:
        JGEXConstructionError: If the clause cannot be added to the problem after max_attempts.

    """
    points: dict[PredicateArgument, JGEXPoint] = {
        PredicateArgument(pt.name): JGEXPoint(x=pt.num.x, y=pt.num.y)
        for pt in problem.points
    }
    default_error_msg = "Did not even attempt to add a clause to the problem"
    last_error = JGEXConstructionError(default_error_msg)
    for attempt in range(max_attempts):
        try:
            clause_consequences = _add_jgex_clause(clause, points, defs, rng)
            return (
                problem.with_new(
                    new_points=_jgex_points_to_newclid_points(
                        clause_consequences.new_points
                    ),
                    new_assumptions=clause_consequences.to_assumptions(),
                ),
                clause_consequences,
            )
        except JGEXConstructionError as e:
            LOGGER.debug(
                f"Failed to add clause to problem {problem.name} (attempt {attempt}): {e}"
            )
            last_error = e
            continue
    raise JGEXConstructionError(
        f"Failed to add clause to problem {problem.name} after {max_attempts} attempts. Last error: {last_error}"
    )


def _jgex_points_to_newclid_points(
    points: dict[PredicateArgument, JGEXPoint],
) -> tuple[Point, ...]:
    return tuple(
        Point(name=PredicateArgument(pname), num=PointNum(x=p.x, y=p.y))
        for pname, p in points.items()
    )


class JGEXClauseConsequences(BaseModel):
    new_points: dict[PredicateArgument, JGEXPoint]
    construction_consequences: list[JGEXConstructionConsequences]
    numerical_requirements: list[PredicateConstruction]

    def to_assumptions(self) -> tuple[PredicateConstruction, ...]:
        return tuple(
            predicate_construction
            for construction_consequence in self.construction_consequences
            for predicate_construction in construction_consequence.to_assumptions()
        )


def rename_points_in_clause_consequences(
    clause_consequences: JGEXClauseConsequences,
    mapping: dict[PredicateArgument, PredicateArgument],
) -> JGEXClauseConsequences:
    return JGEXClauseConsequences(
        new_points={
            mapping[pname]: p for pname, p in clause_consequences.new_points.items()
        },
        construction_consequences=[
            rename_points_in_construction_consequences(
                construction_consequence, mapping
            )
            for construction_consequence in clause_consequences.construction_consequences
        ],
        numerical_requirements=[
            rename_predicate_construction(predicate_construction, mapping)
            for predicate_construction in clause_consequences.numerical_requirements
        ],
    )


def _add_jgex_clause(
    clause: JGEXClause,
    existing_points: dict[PredicateArgument, JGEXPoint],
    defs: dict[str, JGEXDefinition],
    rng: RngGenerator,
) -> JGEXClauseConsequences:
    """Return a new problem with a new clause of construction, e.g. a new excenter."""
    sketches_calls: list[SketchCall] = []
    constructions: list[JGEXConstructionConsequences] = []
    numerical_requirements: list[PredicateConstruction] = []
    for construction in clause.constructions:
        construction_definition = defs.get(construction.name)
        if construction_definition is None:
            if construction.name in {
                num_predicate_type.value
                for num_predicate_type in NUMERICAL_PREDICATES.keys()
            }:
                numerical_requirements.append(
                    PredicateConstruction.from_tuple(
                        (construction.name, *construction.args)
                    )
                )
                continue
            raise JGEXConstructionError(
                f"Construction {construction} has no definition"
            )

        clause_construction, mapping = _add_construction(
            construction=construction,
            construction_definition=construction_definition,
            existing_points=existing_points,
            clause=clause,
        )
        constructions.append(clause_construction)
        sketches_calls.extend(
            SketchCall.from_construction(sketch, mapping)
            for sketch in construction_definition.sketches
        )
    new_points = _add_clause_points(clause, existing_points, sketches_calls, rng)
    return JGEXClauseConsequences(
        construction_consequences=constructions,
        numerical_requirements=numerical_requirements,
        new_points=new_points,
    )


class JGEXConstructionConsequences(BaseModel):
    required_predicates: list[PredicateConstruction]
    added_predicates: list[PredicateConstruction]

    def to_assumptions(self) -> tuple[PredicateConstruction, ...]:
        return tuple(self.required_predicates + self.added_predicates)


def rename_points_in_construction_consequences(
    construction_consequences: JGEXConstructionConsequences,
    mapping: dict[PredicateArgument, PredicateArgument],
) -> JGEXConstructionConsequences:
    return JGEXConstructionConsequences(
        required_predicates=[
            rename_predicate_construction(predicate_construction, mapping)
            for predicate_construction in construction_consequences.required_predicates
        ],
        added_predicates=[
            rename_predicate_construction(predicate_construction, mapping)
            for predicate_construction in construction_consequences.added_predicates
        ],
    )


def _add_construction(
    construction: JGEXConstruction,
    construction_definition: JGEXDefinition,
    existing_points: dict[PredicateArgument, JGEXPoint],
    clause: JGEXClause,
) -> tuple[
    JGEXConstructionConsequences,
    dict[JGEXVariableName, PredicateArgument],
]:
    added: list[PredicateConstruction] = []
    mapping = mapping_from_construction(construction, construction_definition)

    # Ensure that all input points exist
    for input_point in construction_definition.input_points:
        required_point = mapping.get(input_point)
        if required_point is None:
            raise ValueError(
                f"Definition {construction_definition.name.value} has input point {input_point} that is missing from mapping {mapping}. "
                f"This is probably just because the definition {construction_definition.name.name} error itself is wrong and should be fixed."
            )
        if required_point not in existing_points:
            raise ValueError(
                f"Construction '{construction}' with mapping {mapping}"
                f" requires input point '{required_point}' that does not exist yet: {list(existing_points.keys())}."
            )

    required: list[PredicateConstruction] = []
    for requirement in construction_definition.requirements.constructions:
        if len(requirement.args) == 0:
            continue
        required.append(
            _jgex_construction_to_predicate_construction(requirement, mapping)
        )

    for clause in construction_definition.clauses:
        for construction in clause.constructions:
            added.append(
                _jgex_construction_to_predicate_construction(construction, mapping)
            )

    construction_consequences = JGEXConstructionConsequences(
        required_predicates=required, added_predicates=added
    )
    return construction_consequences, mapping


def _jgex_construction_to_predicate_construction(
    construction: JGEXConstruction,
    mapping: dict[JGEXVariableName, PredicateArgument],
) -> PredicateConstruction:
    args: tuple[PredicateArgument, ...] = tuple(  # type: ignore
        mapping.get(arg, arg)  # type: ignore
        for arg in construction.args
    )
    return PredicateConstruction.from_predicate_type_and_args(
        PredicateType(construction.name), args
    )


def _add_clause_points(
    clause: JGEXClause,
    existing_points: dict[PredicateArgument, JGEXPoint],
    sketches_calls: list[SketchCall],
    rng: RngGenerator,
) -> dict[PredicateArgument, JGEXPoint]:
    new_fixed_points: dict[PredicateArgument, JGEXPoint | None] = {}
    for point_value in clause.points:
        if "@" in point_value:
            name, pos = atomize(point_value, "@")
            x, y = atomize(pos, "_")
            new_fixed_points[PredicateArgument(name)] = JGEXPoint(
                x=float(x), y=float(y)
            )
        else:
            new_fixed_points[PredicateArgument(point_value)] = None

    for pname in new_fixed_points:
        if pname in existing_points:
            raise JGEXConstructionError(
                f"Clause {clause} cannot be added because it creates point {pname} that already exists. "
                f"Current points are {list(existing_points.keys())}."
            )

    new_sketch_points = _sketch_new_numerical_points(
        sketches_calls, existing_points, rng
    )
    for (pname, fixed_point), sketch_point in zip(
        new_fixed_points.items(), new_sketch_points
    ):
        if fixed_point is None:
            new_fixed_points[pname] = sketch_point

    new_points = {pname: p for pname, p in new_fixed_points.items() if p is not None}
    _ensure_numerical_points_are_valid(new_points, existing_points)
    return new_points


def _sketch_new_numerical_points(
    sketches_calls: list[SketchCall],
    existing_points: dict[PredicateArgument, JGEXPoint],
    rng: RngGenerator,
) -> list[JGEXPoint]:
    to_be_intersected: list[JGEXGeometry] = []
    for sketch_call in sketches_calls:
        args: list[JGEXPoint | PredicateArgument] = []
        for arg in sketch_call.args:
            if is_numerical_argument(arg):
                # Handle numerical arguments
                args.append(PredicateArgument(arg))
            else:
                # Handle point names
                args.append(existing_points[arg])
        to_be_intersected += sketch(name=sketch_call.name, args=tuple(args), rng=rng)
    return reduce_intersection(
        to_be_intersected, list(existing_points.values()), rng=rng
    )


def _ensure_numerical_points_are_valid(
    new_points: dict[PredicateArgument, JGEXPoint],
    existing_points: dict[PredicateArgument, JGEXPoint],
) -> None:
    ensure_not_too_close_numerical(new_points, existing_points)
    ensure_not_too_far_numerical(new_points, existing_points)
