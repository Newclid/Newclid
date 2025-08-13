from __future__ import annotations

from fractions import Fraction
from typing import Literal

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Segment
from newclid.tools import fraction_to_len, str_to_fraction


class SquaredConstantLength(PredicateInterface):
    """l2const A B L -
    Represent that the square of the length of segment AB is L

    L should be given as a float.
    """

    predicate_type: Literal[PredicateType.SQUARED_CONSTANT_LENGTH] = (
        PredicateType.SQUARED_CONSTANT_LENGTH
    )
    segment: Segment
    square_length: Fraction

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, slength = args
        if a == b:
            return None
        a, b = sorted((a, b))
        return (a, b, PredicateArgument(fraction_to_len(str_to_fraction(slength))))

    def check_numerical(self) -> bool:
        a, b = self.segment
        slength = self.square_length
        squared_length = (a.num - b.num).dot(a.num - b.num)
        return close_enough(squared_length, float(slength))

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        a, b = self.segment
        return (
            PredicateArgument(a.name),
            PredicateArgument(b.name),
            PredicateArgument(fraction_to_len(self.square_length)),
        )

    def __str__(self) -> str:
        a, b = self.segment
        return f"|{a}{b}|\u00b2 = {fraction_to_len(self.square_length)}"
