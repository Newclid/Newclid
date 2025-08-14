from __future__ import annotations

from typing import Literal

from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Point, Segment


class MidPoint(PredicateInterface):
    """midp M A B -
    Represent that M is the midpoint of the segment AB.

    Can be equivalent to coll M A B and cong A M B M."""

    predicate_type: Literal[PredicateType.MIDPOINT] = PredicateType.MIDPOINT
    segment: Segment
    midpoint: Point

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        if len(set(args)) != 3:
            return None
        m, a, b = args
        a, b = sorted((a, b))
        return (m, a, b)

    def check_numerical(self) -> bool:
        a, b = self.segment
        return self.midpoint.num.close_enough((a.num + b.num) / 2)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        a, b = self.segment
        return (
            PredicateArgument(self.midpoint.name),
            PredicateArgument(a.name),
            PredicateArgument(b.name),
        )

    def __str__(self) -> str:
        a, b = self.segment
        return f"{self.midpoint} is the midpoint of {a}{b}"
