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


class MidpointHeuristicConfig(BaseModel):
    heuristic_name: Literal[HeuristicName.MIDPOINT] = HeuristicName.MIDPOINT


class MidpointHeuristic(Heuristic):
    """Adds a number of midpoints of pairs of points present in the JGEXProblem."""

    def new_clauses(
        self,
        setup: HeuristicSetup,
        max_new_points: int,
        rng: numpy.random.Generator,
    ) -> list[JGEXClause]:
        pairs_of_points = list(itertools.combinations(setup.points, 2))
        added_midpoints: list[PredicateArgument] = []
        new_clauses: list[JGEXClause] = []
        for _ in range(max_new_points):
            if not pairs_of_points:
                break

            # Randomly select a pair of points to create a midpoint
            pair_index = rng.choice(len(pairs_of_points))
            p1, p2 = pairs_of_points.pop(pair_index)

            new_point = get_available_from_alphabet(
                list(setup.points) + added_midpoints
            )
            if new_point is None:
                LOGGER.warning(
                    "No available points left in the alphabet, skipping midpoint addition."
                )
                break

            added_midpoints.append(new_point)

            new_clause_string = f"{new_point} = midpoint {new_point} {p1} {p2}"
            new_clauses.append(JGEXClause.from_str(new_clause_string)[0])

        return new_clauses
