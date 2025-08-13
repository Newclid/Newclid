from __future__ import annotations

import itertools
from typing import Literal

from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import NumericalPredicate
from newclid.symbols.points_registry import Point


class Diff(NumericalPredicate):
    """diff a b -

    Represent that a is not equal to b.

    Numerical only.
    """

    predicate_type: Literal[PredicateType.DIFFERENT] = PredicateType.DIFFERENT
    points: tuple[Point, ...]

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        return tuple(sorted(args))

    def check_numerical(self) -> bool:
        existing_points = [p for p in self.points]
        for p, q in itertools.combinations(existing_points, 2):
            if p.num.close_enough(q.num):
                return False
        return True

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.points)

    def __str__(self) -> str:
        if len(self.points) == 2:
            return f"{self.points[0]} ≠ {self.points[1]}"
        else:
            return f"{', '.join(str(p) for p in self.points)} are all distinct"
