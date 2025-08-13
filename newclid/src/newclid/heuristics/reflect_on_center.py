import logging
from typing import Literal

import numpy
from pydantic import BaseModel

from newclid.heuristics._index import HeuristicName
from newclid.heuristics._interface import Heuristic, HeuristicSetup
from newclid.heuristics.alphabet import get_available_from_alphabet
from newclid.jgex.clause import JGEXClause

LOGGER = logging.getLogger(__name__)


class ReflectOnCenterHeuristicConfig(BaseModel):
    heuristic_name: Literal[HeuristicName.REFLECT_ON_CENTER] = (
        HeuristicName.REFLECT_ON_CENTER
    )


class ReflectOnCenterHeuristic(Heuristic):
    """Reflect points on the center of a circle."""

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

            p1 = circle.points[0]
            p2 = circle.points[1]
            p3 = circle.points[2]

            new_center = get_available_from_alphabet(points)
            if new_center is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping reflection on this center."
                )
                continue

            points.append(new_center)

            new_clause_string = f"{new_center} = foot {new_center} {p1} {p2} {p3}"
            new_clause = JGEXClause.from_str(new_clause_string)[0]
            new_clauses.append(new_clause)

            # Reflect all points on the center of the circle
            for point in circle.points:
                new_point = get_available_from_alphabet(points)
                if new_point is None:
                    LOGGER.warning(
                        "No available points left in the alphabet, skipping reflection addition."
                    )
                    continue
                points.append(new_point)

                new_clause_string = (
                    f"{new_point} = mirror {new_point} {point} {new_center}"
                )
                new_clause = JGEXClause.from_str(new_clause_string)[0]
                new_clauses.append(new_clause)

        return new_clauses
