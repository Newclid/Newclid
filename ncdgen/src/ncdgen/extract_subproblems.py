# coding: utf-8
from __future__ import annotations

from typing import Iterable, TypeVar

from newclid.jgex.clause import JGEXClause, order_clauses_by_points_construction_order
from newclid.jgex.constructions import ALL_JGEX_CONSTRUCTIONS_BY_NAME
from newclid.jgex.definition import input_points_of_clause
from newclid.jgex.formulation import JGEXFormulation
from newclid.justifications._index import JustificationType
from newclid.problem import predicate_to_construction

from ncdgen.aux_discriminators._interface import AuxDiscriminator
from ncdgen.build_diagram import Diagram

T = TypeVar("T")


def extract_subproblems_and_their_dependencies(
    diagram: Diagram, aux_discriminator: AuxDiscriminator
) -> list[JGEXFormulation]:
    """Get all problem dependencies and their setup and aux point sets.

    Args:
        diagram: The Diagram dataclass containing the graph, problem, dependencies and setup graph
        rules: The rules to use for solving
        aux_only: If True, only return dependencies that have nonempty aux sets
        return_added_deps: If True, also return the added dependencies

    Returns:
        If return_added_deps is False:
            Tuple of (dependencies, setup_points, aux_points)
        If return_added_deps is True:
            Tuple of (dependencies, setup_points, aux_points, added_dependencies)
    """
    subproblems: list[JGEXFormulation] = []
    goals_with_aux = aux_discriminator.goals_with_aux_setup_split(diagram)
    for goal, points_for_goal in goals_with_aux.items():
        if goal.dependency_type not in (
            JustificationType.RULE_APPLICATION,
            JustificationType.DIRECT_CONSEQUENCE,
            JustificationType.AR_DEDUCTION,
        ):
            continue
        constructed: set[str] = set()
        setup_clauses = _get_clauses_for_points(
            points_for_goal.setup_points, diagram.jgex_problem.clauses, constructed
        )
        aux_clauses = _get_clauses_for_points(
            points_for_goal.aux_points, diagram.jgex_problem.clauses, constructed
        )
        goal_construction = predicate_to_construction(goal.predicate)
        subproblems.append(
            JGEXFormulation(
                name=f"Prove {goal.predicate}",
                setup_clauses=tuple(setup_clauses),
                auxiliary_clauses=tuple(aux_clauses),
                goals=(goal_construction,),
            )
        )
    return subproblems


def _get_clauses_for_points(
    points: set[str],
    problem_clauses: Iterable[JGEXClause],
    constructed: set[str],
) -> list[JGEXClause]:
    """For a given point set (setup or aux), return the problem clauses that construct the points.

    The clauses are returned in the order of the construction order of the points.

    Args:
        points: The points to get clauses for
        problem_clauses: The problem clauses to search through
        constructed: The points that have already been constructed

    Returns:
        The problem clauses that construct the points.
    """
    clauses: list[JGEXClause] = []
    required_points = points.copy()
    while required_points:
        point = required_points.pop()
        if point in constructed:
            continue
        cl = [clause for clause in problem_clauses if point in clause.points]
        if not cl:
            raise IndexError(f"cannot find point {point} in any problem clause")
        if len(cl) > 1:
            raise IndexError(f"point {point} appears in multiple independent clauses")
        clause = cl[0]
        clauses.append(clause)
        constructed.update(clause.points)

        # Add the points that are required to construct the points in the clause
        input_points = input_points_of_clause(clause, ALL_JGEX_CONSTRUCTIONS_BY_NAME)
        required_points.update(
            p for p in input_points if p not in constructed and p not in points
        )

    return order_clauses_by_points_construction_order(clauses)
