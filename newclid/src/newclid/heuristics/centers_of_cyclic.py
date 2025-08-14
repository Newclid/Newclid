import logging
from typing import Literal

import numpy
from pydantic import BaseModel

from newclid.heuristics._index import HeuristicName
from newclid.heuristics._interface import Heuristic, HeuristicSetup
from newclid.heuristics.alphabet import get_available_from_alphabet
from newclid.jgex.clause import JGEXClause

LOGGER = logging.getLogger(__name__)


class CentersOfCyclicHeuristicConfig(BaseModel):
    heuristic_name: Literal[HeuristicName.CENTERS] = HeuristicName.CENTERS


class CentersOfCyclicHeuristic(Heuristic):
    """Add all centers of circles with three points."""

    def new_clauses(
        self,
        setup: HeuristicSetup,
        max_new_points: int,
        rng: numpy.random.Generator,
    ) -> list[JGEXClause]:
        circles = list(setup.circles)
        points = list(setup.points)
        new_clauses: list[JGEXClause] = []

        for _ in range(max_new_points):
            if not circles:
                break

            circle_index = rng.choice(len(circles))
            circle = circles.pop(circle_index)

            p1, p2, p3 = sorted(circle.points[:3])

            new_point = get_available_from_alphabet(points)
            if new_point is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping center addition."
                )
                continue
            points.append(new_point)
            new_clause_string = f"{new_point} = circle {new_point} {p1} {p2} {p3}"
            new_clause = JGEXClause.from_str(new_clause_string)[0]
            new_clauses.append(new_clause)

        return new_clauses
