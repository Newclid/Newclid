from __future__ import annotations

from fractions import Fraction
from typing import TYPE_CHECKING, Literal, Optional

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Segment
from newclid.tools import fraction_to_len, get_quotient, str_to_fraction

if TYPE_CHECKING:
    from newclid.proof_state import ProofState


class ConstantLength(PredicateInterface):
    """lconst A B L -
    Represent that the length of segment AB is L

    L should be given as a float.
    """

    predicate_type: Literal[PredicateType.CONSTANT_LENGTH] = (
        PredicateType.CONSTANT_LENGTH
    )
    segment: Segment
    length: Fraction

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, length = args
        if a == b:
            return None
        a, b = sorted((a, b))
        return (a, b, PredicateArgument(fraction_to_len(str_to_fraction(length))))

    def check_numerical(self) -> bool:
        a, b = self.segment
        actual_length = a.num.distance(b.num)
        return close_enough(actual_length, float(self.length))

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        a, b = self.segment
        return (
            PredicateArgument(a.name),
            PredicateArgument(b.name),
            PredicateArgument(fraction_to_len(self.length)),
        )

    def __str__(self) -> str:
        a, b = self.segment
        return f"{a}{b} = {fraction_to_len(self.length)}"


class LCompute(PredicateInterface):
    """lcompute A B"""

    predicate_type: Literal[PredicateType.L_COMPUTE] = PredicateType.L_COMPUTE
    segment: Segment

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> Optional[tuple[PredicateArgument, ...]]:
        a, b = args
        if a == b:
            return None
        return tuple(sorted((a, b)))

    def check_numerical(self) -> bool:
        return True  # Can always compute length

    def check(self, proof_state: ProofState) -> bool:
        lconst = lconst_from_lcompute(self)
        return proof_state.check(lconst)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.segment)

    def __str__(self) -> str:
        return str(lconst_from_lcompute(self))


def lconst_from_lcompute(lcompute: LCompute) -> ConstantLength:
    a, b = lcompute.segment
    length = get_quotient(a.num.distance(b.num))
    return ConstantLength(segment=(a, b), length=length)
