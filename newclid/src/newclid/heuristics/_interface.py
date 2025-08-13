from abc import ABC, abstractmethod

import numpy
from pydantic import BaseModel

from newclid.heuristics.geometric_objects import (
    AngleHeuristic,
    CircleHeuristic,
    LineHeuristic,
)
from newclid.jgex.clause import JGEXClause
from newclid.predicate_types import PredicateArgument
from newclid.problem import PredicateConstruction


class HeuristicSetup(BaseModel):
    """Problem given to a heuristic to deduce new JGEX clauses."""

    points: tuple[PredicateArgument, ...]
    free_points: tuple[PredicateArgument, ...]
    lines: tuple[LineHeuristic, ...]
    circles: tuple[CircleHeuristic, ...]
    angles: tuple[AngleHeuristic, ...]
    goals: tuple[PredicateConstruction, ...]


class Heuristic(ABC):
    @abstractmethod
    def new_clauses(
        self,
        setup: HeuristicSetup,
        max_new_points: int,
        rng: numpy.random.Generator,
    ) -> list[JGEXClause]:
        """Find new clauses to add to the problem by applying the heuristic."""
