from __future__ import annotations

from fractions import Fraction
from typing import TYPE_CHECKING, Literal

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.predicates.constant_angle import ACompute
from newclid.symbols.points_registry import Ratio
from newclid.tools import fraction_to_ratio, get_quotient, str_to_fraction

if TYPE_CHECKING:
    from newclid.proof_state import ProofState


class ConstantRatio(PredicateInterface):
    """rconst A B C D r -
    Represent that AB / CD = r

    r should be given with numerator and denominator separated by '/', as in 2/3.
    """

    predicate_type: Literal[PredicateType.CONSTANT_RATIO] = PredicateType.CONSTANT_RATIO
    ratio: Ratio
    value: Fraction

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, c, d, r = args
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
        (a, b), (c, d) = self.ratio
        ratio = a.num.distance(b.num) / c.num.distance(d.num)
        return close_enough(ratio, float(self.value))

    def __str__(self) -> str:
        (a, b), (c, d) = self.ratio
        return f"{a}{b}:{c}{d} = {fraction_to_ratio(self.value)}"

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        (a, b), (c, d) = self.ratio
        return (
            PredicateArgument(a.name),
            PredicateArgument(b.name),
            PredicateArgument(c.name),
            PredicateArgument(d.name),
            PredicateArgument(fraction_to_ratio(self.value)),
        )


class RCompute(PredicateInterface):
    """rcompute A B C D"""

    predicate_type: Literal[PredicateType.R_COMPUTE] = PredicateType.R_COMPUTE

    ratio: Ratio

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        return ACompute.preparse(args)

    def check_numerical(self) -> bool:
        return True  # Can always compute ratio

    def check(self, proof_state: ProofState) -> bool | None:
        rconst = rconst_from_rcompute(self)
        return proof_state.check(rconst)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(
            PredicateArgument(p.name) for segment in self.ratio for p in segment
        )

    def __str__(self) -> str:
        return str(rconst_from_rcompute(self))


def rconst_from_rcompute(rcompute: RCompute) -> ConstantRatio:
    (a, b), (c, d) = rcompute.ratio
    ratio = get_quotient(a.num.distance(b.num) / c.num.distance(d.num))
    return ConstantRatio(ratio=rcompute.ratio, value=ratio)
