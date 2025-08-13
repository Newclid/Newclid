from __future__ import annotations

from fractions import Fraction
from typing import TYPE_CHECKING, Literal

from numpy import pi

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Line, Point, Segment
from newclid.symbols.symbols_registry import LineOrCircle, SymbolsRegistry
from newclid.tools import fraction_to_angle, get_quotient, str_to_fraction

if TYPE_CHECKING:
    from newclid.proof_state import ProofState


def angle_between_4_points(a: Point, b: Point, c: Point, d: Point):
    return ((d.num - c.num).angle() - (b.num - a.num).angle()) % pi


class ConstantAngle(PredicateInterface):
    """aconst AB CD Y -
    Represent that the rotation needed to go from line AB to line CD,
    oriented on the clockwise direction is Y.

    The syntax of Y is either a fraction of pi like 2pi/3 for radians
    or a number followed by a 'o' like 120o for degrees.
    """

    predicate_type: Literal[PredicateType.CONSTANT_ANGLE] = PredicateType.CONSTANT_ANGLE

    line1: Line
    line2: Line
    angle: Fraction

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, c, d, y = args
        if a == b or c == d:
            return None
        a, b = sorted((a, b))
        c, d = sorted((c, d))
        f = str_to_fraction(y)
        f %= 1
        return (a, b, c, d, PredicateArgument(fraction_to_angle(f)))

    def check_numerical(self) -> bool:
        a, b, c, d = self.line1 + self.line2
        angle_value = angle_between_4_points(a, b, c, d)
        expected_value = float(self.angle) * pi % pi
        return close_enough(angle_value, expected_value)

    def symbols(self, symbols: SymbolsRegistry) -> tuple[LineOrCircle, ...]:
        a, b = self.line1
        l1 = symbols.lines.line_thru_pair(a, b)
        c, d = self.line2
        l2 = symbols.lines.line_thru_pair(c, d)
        return (l1, l2)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        a, b = self.line1
        c, d = self.line2
        return (
            PredicateArgument(a.name),
            PredicateArgument(b.name),
            PredicateArgument(c.name),
            PredicateArgument(d.name),
            PredicateArgument(fraction_to_angle(self.angle)),
        )

    def __str__(self) -> str:
        a, b = self.line1
        c, d = self.line2
        return f"∠({a}{b},{c}{d}) = {fraction_to_angle(self.angle)}"


class ACompute(PredicateInterface):
    """acompute AB CD"""

    predicate_type: Literal[PredicateType.A_COMPUTE] = PredicateType.A_COMPUTE

    segment1: Segment
    segment2: Segment

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, c, d = args
        if a == b or c == d:
            return None
        a, b = sorted((a, b))
        c, d = sorted((c, d))
        return (a, b, c, d)

    def check_numerical(self) -> bool:
        a, b, c, d = self.segment1 + self.segment2
        ang = angle_between_4_points(a, b, c, d)
        if close_enough(ang, pi):
            ang = 0
        get_quotient(ang / pi)
        return True

    def check(self, proof_state: ProofState) -> bool:
        aconst = aconst_from_acompute(self)
        return proof_state.check(aconst)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.segment1 + self.segment2)

    def __str__(self) -> str:
        aconst = aconst_from_acompute(self)
        return str(aconst)


def aconst_from_acompute(acompute: ACompute) -> ConstantAngle:
    a, b, c, d = acompute.segment1 + acompute.segment2
    y = get_quotient(angle_between_4_points(a, b, c, d) / pi)
    return ConstantAngle(line1=(a, b), line2=(c, d), angle=y)
