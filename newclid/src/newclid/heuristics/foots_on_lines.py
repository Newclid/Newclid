import itertools
import logging
from typing import Literal

import numpy
from pydantic import BaseModel

from newclid.heuristics._index import HeuristicName
from newclid.heuristics._interface import Heuristic, HeuristicSetup
from newclid.heuristics.alphabet import get_available_from_alphabet
from newclid.jgex.clause import JGEXClause

LOGGER = logging.getLogger(__name__)


class FootHeuristicConfig(BaseModel):
    heuristic_name: Literal[HeuristicName.FOOT] = HeuristicName.FOOT


class FootHeuristic(Heuristic):
    """Add foot points on lines."""

    def new_clauses(
        self,
        setup: HeuristicSetup,
        max_new_points: int,
        rng: numpy.random.Generator,
    ) -> list[JGEXClause]:
        points = list(setup.points)
        pairs_of_points = list(itertools.combinations(points, 2))
        unflattened_triplets = itertools.product(points, pairs_of_points)
        triplets_of_points = [(a, b, c) for a, (b, c) in unflattened_triplets]
        new_clauses: list[JGEXClause] = []

        for _ in range(max_new_points):
            if not triplets_of_points:
                break

            triplet_index = rng.choice(len(triplets_of_points))
            p3, p1, p2 = triplets_of_points.pop(triplet_index)

            new_point = get_available_from_alphabet(points)
            if new_point is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping foot point addition."
                )
                break

            points.append(new_point)
            new_clause_string = f"{new_point} = foot {new_point} {p3} {p1} {p2}"
            new_clause = JGEXClause.from_str(new_clause_string)[0]
            new_clauses.append(new_clause)

        return new_clauses
