from __future__ import annotations

from typing import Literal

from newclid.numerical import nearly_zero
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import NumericalPredicate, PredicateInterface
from newclid.symbols.points_registry import Line
from newclid.symbols.symbols_registry import LineOrCircle, SymbolsRegistry


class Perp(PredicateInterface):
    """perp A B C D -
    Represent that the line AB is perpendicular to the line CD.
    """

    predicate_type: Literal[PredicateType.PERPENDICULAR] = PredicateType.PERPENDICULAR
    line1: Line
    line2: Line

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, c, d = args
        if a == b or c == d:
            return None
        a, b = sorted((a, b))
        c, d = sorted((c, d))
        if (a, b) > (c, d):
            a, b, c, d = c, d, a, b
        return (a, b, c, d)

    def check_numerical(self) -> bool:
        a, b = self.line1
        c, d = self.line2
        return nearly_zero((a.num - b.num).dot(c.num - d.num))

    def symbols(self, symbols: SymbolsRegistry) -> tuple[LineOrCircle, ...]:
        l1 = symbols.lines.line_thru_pair(*self.line1)
        l2 = symbols.lines.line_thru_pair(*self.line2)
        return (l1, l2)

    def to_constructive(self, point: str) -> str:
        a, b = [p.name for p in self.line1]
        c, d = [p.name for p in self.line2]
        if point in [c, d]:
            a, b, c, d = c, d, a, b
        if point == b:
            a, b = b, a
        if point == d:
            c, d = d, c
        if a == c and a == point:
            return f"on_dia {a} {b} {d}"
        return f"on_tline {a} {b} {c} {d}"

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.line1 + self.line2)

    def __str__(self) -> str:
        a, b = self.line1
        c, d = self.line2
        return f"{a}{b} ⟂ {c}{d}"


class NPerp(NumericalPredicate):
    """nperp A B C D -
    Represent that lines AB and CD are NOT perpendicular.

    Numerical only.
    """

    predicate_type: Literal[PredicateType.N_PERPENDICULAR] = (
        PredicateType.N_PERPENDICULAR
    )

    line1: Line
    line2: Line

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        return Perp.preparse(args)

    def check_numerical(self) -> bool:
        return not Perp(line1=self.line1, line2=self.line2).check_numerical()

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.line1 + self.line2)

    def __str__(self) -> str:
        a, b = self.line1
        c, d = self.line2
        return f"{a}{b} ⟂̸ {c}{d}"
