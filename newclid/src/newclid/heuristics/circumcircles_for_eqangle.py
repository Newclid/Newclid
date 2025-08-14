import logging
from typing import Literal

import numpy as np
from pydantic import BaseModel

from newclid.heuristics._index import HeuristicName
from newclid.heuristics._interface import Heuristic, HeuristicSetup
from newclid.heuristics.alphabet import get_available_from_alphabet
from newclid.heuristics.geometric_objects import LineHeuristic
from newclid.jgex.clause import JGEXClause
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType

LOGGER = logging.getLogger(__name__)


class ThreeCircumcirclesForEqangleGoalHeuristicConfig(BaseModel):
    heuristic_name: Literal[HeuristicName.THREE_CIRCUMCIRCLES_FOR_EQANGLE_GOAL] = (
        HeuristicName.THREE_CIRCUMCIRCLES_FOR_EQANGLE_GOAL
    )


class ThreeCircumcirclesForEqangleGoalHeuristic(Heuristic):
    """
    Given an eqangle goal, create the vertices and implement the two versions of the 3 circumcircles method for the corresponding quadrilateral configuration.

    Check the solution of "Langley's Adventious Angles" problem for more details.
    """

    def new_clauses(
        self,
        setup: HeuristicSetup,
        max_new_points: int,
        rng: np.random.Generator,
    ) -> list[JGEXClause]:
        i = 0
        eqangle_goals = [
            g for g in setup.goals if g.predicate_type == PredicateType.EQUAL_ANGLES
        ]
        added_points: list[PredicateArgument] = []
        new_clauses: list[JGEXClause] = []

        while i < max_new_points and eqangle_goals:
            goal_index = rng.choice(len(eqangle_goals))
            goal = eqangle_goals.pop(goal_index)

            line_matrix: list[list[LineHeuristic]] = [
                [LineHeuristic(points=()), LineHeuristic(points=())],
                [LineHeuristic(points=()), LineHeuristic(points=())],
            ]

            for line in setup.lines:
                if goal.args[0] in line.points and goal.args[1] in line.points:
                    line_matrix[0][0] = line
                if goal.args[2] in line.points and goal.args[3] in line.points:
                    line_matrix[0][1] = line
                if goal.args[4] in line.points and goal.args[5] in line.points:
                    line_matrix[1][0] = line
                if goal.args[6] in line.points and goal.args[7] in line.points:
                    line_matrix[1][1] = line

            # TODO: Clarify what this does
            vertices: list[PredicateArgument] = []
            for j in [0, 2]:
                for k in [4, 6]:
                    line_0 = line_matrix[0][int(j % 2)]
                    line_1 = line_matrix[1][int((k / 2) % 2)]
                    if set(line_0.points) & set(line_1.points):
                        existing_vertex = next(
                            iter(set(line_0.points) & set(line_1.points))
                        )
                        vertices.append(existing_vertex)
                    else:
                        vertex = get_available_from_alphabet(
                            list(setup.points) + added_points
                        )
                        if vertex is None:
                            LOGGER.warning(
                                "No available points left in the alphabet, skipping vertex addition."
                            )
                            continue
                        added_points.append(vertex)

                        new_clause_string = f"{vertex} = on_line {vertex} {goal.args[j]} {goal.args[j + 1]}, on_line {vertex} {goal.args[k]} {goal.args[k + 1]}"
                        new_clause = JGEXClause.from_str(new_clause_string)[0]
                        new_clauses.append(new_clause)

            i += 4

            if len(vertices) < 4:
                LOGGER.warning(
                    "Not enough vertices created for the full construction. We stop here."
                )
                continue

            centers: list[PredicateArgument] = []
            center_1 = get_available_from_alphabet(list(setup.points) + added_points)
            if center_1 is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping center addition."
                )
            else:
                added_points.append(center_1)
                new_clause_string = f"{center_1} = circle {center_1} {vertices[1]} {vertices[2]} {vertices[0]}"
                new_clause = JGEXClause.from_str(new_clause_string)[0]
                new_clauses.append(new_clause)

            center_2 = get_available_from_alphabet(list(setup.points) + added_points)
            if center_2 is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping center addition."
                )
            else:
                added_points.append(center_2)
                new_clause_string = f"{center_2} = circle {center_2} {vertices[1]} {vertices[2]} {vertices[3]}"
                new_clause = JGEXClause.from_str(new_clause_string)[0]
                new_clauses.append(new_clause)

            i += 2
            if len(centers) < 2:
                LOGGER.warning(
                    "Not enough centers created for the full construction. We stop here."
                )
                continue

            center_3 = get_available_from_alphabet(list(setup.points) + added_points)
            if center_3 is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping center addition."
                )
            else:
                added_points.append(center_3)
                new_clause_string = f"{center_3} = circle {center_3} {center_1} {center_2} {vertices[1]}"
                new_clause = JGEXClause.from_str(new_clause_string)[0]
                new_clauses.append(new_clause)

            center_4 = get_available_from_alphabet(list(setup.points) + added_points)
            if center_4 is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping center addition."
                )
            else:
                added_points.append(center_4)
                new_clause_string = f"{center_4} = circle {center_4} {center_1} {center_2} {vertices[2]}"
                new_clause = JGEXClause.from_str(new_clause_string)[0]
                new_clauses.append(new_clause)

            i += 2

        return new_clauses
