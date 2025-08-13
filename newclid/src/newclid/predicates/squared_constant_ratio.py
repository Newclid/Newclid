from __future__ import annotations

from fractions import Fraction
from typing import Literal

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Segment
from newclid.tools import fraction_to_ratio, str_to_fraction


class SquaredConstantRatio(PredicateInterface):
    """r2const A B C D r -
    Represent that |AB|² / |CD|² = r

    r should be given with numerator and denominator separated by '/', as in 2/3.
    """

    predicate_type: Literal[PredicateType.SQUARED_CONSTANT_RATIO] = (
        PredicateType.SQUARED_CONSTANT_RATIO
    )
    segment1: Segment
    segment2: Segment
    square_ratio: Fraction

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        try:
            a, b, c, d, r = args
        except ValueError:
            raise ValueError(f"Invalid arguments: {args}")
        if a == b or c == d:
            return None
        f = str_to_fraction(r)
        a, b = sorted((a, b))
        c, d = sorted((c, d))
        if (a, b) > (c, d):
            a, b, c, d = c, d, a, b
            f = 1 / f
        return (a, b, c, d, PredicateArgument(fraction_to_ratio(f)))

    def check_numerical(self) -> bool:
        a, b = self.segment1
        c, d = self.segment2
        r = self.square_ratio
        numerator = (a.num - b.num).dot(a.num - b.num)
        denominator = (c.num - d.num).dot(c.num - d.num)
        return close_enough(numerator / denominator, float(r))

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        a, b = self.segment1
        c, d = self.segment2
        r = self.square_ratio
        return (
            PredicateArgument(a.name),
            PredicateArgument(b.name),
            PredicateArgument(c.name),
            PredicateArgument(d.name),
            PredicateArgument(fraction_to_ratio(r)),
        )

    def __str__(self) -> str:
        a, b = self.segment1
        c, d = self.segment2
        r = self.square_ratio
        return f"|{a}{b}|\u00b2:|{c}{d}|\u00b2 = {fraction_to_ratio(r)}"
