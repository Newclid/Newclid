import itertools
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


class LineIntersectionsHeuristicConfig(BaseModel):
    heuristic_name: Literal[HeuristicName.LINE_INTERSECTIONS] = (
        HeuristicName.LINE_INTERSECTIONS
    )


class LineIntersectionsHeuristic(Heuristic):
    """Add intersection points between lines."""

    def new_clauses(
        self,
        setup: HeuristicSetup,
        max_new_points: int,
        rng: numpy.random.Generator,
    ) -> list[JGEXClause]:
        pairs_of_lines = list(itertools.combinations(setup.lines, 2))
        added_points: list[PredicateArgument] = []
        new_clauses: list[JGEXClause] = []

        for _ in range(max_new_points):
            if not pairs_of_lines:
                break

            pair_index = rng.choice(len(pairs_of_lines))
            line1, line2 = pairs_of_lines.pop(pair_index)

            point_1 = line1.points[0]
            point_2 = line1.points[1]

            point_3 = line2.points[0]
            point_4 = line2.points[1]

            new_point = get_available_from_alphabet(list(setup.points) + added_points)
            if new_point is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping intersection addition."
                )
                break

            added_points.append(new_point)

            new_clause_string = f"{new_point} = on_line {new_point} {point_1} {point_2}, on_line {new_point} {point_3} {point_4}"
            new_clause = JGEXClause.from_str(new_clause_string)[0]
            new_clauses.append(new_clause)

        return new_clauses
