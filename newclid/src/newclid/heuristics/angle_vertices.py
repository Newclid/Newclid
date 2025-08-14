import logging
from typing import Literal

import numpy
from pydantic import BaseModel

from newclid.heuristics._index import HeuristicName
from newclid.heuristics._interface import Heuristic, HeuristicSetup
from newclid.heuristics.alphabet import get_available_from_alphabet
from newclid.jgex.clause import JGEXClause
from newclid.predicate_types import PredicateArgument

LOGGER = logging.getLogger(__name__)


class AngleVerticesHeuristicConfig(BaseModel):
    heuristic_name: Literal[HeuristicName.ANGLE_VERTICES] = HeuristicName.ANGLE_VERTICES


class AngleVerticesHeuristic(Heuristic):
    """
    Add all angle vertices defined at the predicate of the JGEX problem.

    Args:
        problem (JGEXProblem): The JGEX problem to which angle vertices will be added.
        angles (List): A list of initial angles defined in the JGEX problem.

    Returns:
        JGEXProblem: The modified JGEX problem with added angle vertices.
    """

    def new_clauses(
        self,
        setup: HeuristicSetup,
        max_new_points: int,
        rng: numpy.random.Generator,
    ) -> list[JGEXClause]:
        angles = list(setup.angles)

        added_points: list[PredicateArgument] = []
        new_clauses: list[JGEXClause] = []
        for _index in range(max_new_points):
            if not angles:
                break

            angle_index = rng.choice(len(angles))
            angle = angles.pop(angle_index)

            point_1 = angle.line_1[0]
            point_2 = angle.line_1[1]
            point_3 = angle.line_2[0]
            point_4 = angle.line_2[1]

            new_point = get_available_from_alphabet(list(setup.points) + added_points)
            if new_point is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping angle vertex addition."
                )
                break

            added_points.append(new_point)
            new_clause_string = f"{new_point} = on_line {new_point} {point_1} {point_2}, on_line {new_point} {point_3} {point_4}"
            new_clause = JGEXClause.from_str(new_clause_string)[0]
            new_clauses.append(new_clause)

        return new_clauses
