from __future__ import annotations

from typing import Literal

import numpy as np

from newclid.numerical import close_enough
from newclid.numerical.geometries import line_num_from_points
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import NumericalPredicate, PredicateInterface
from newclid.predicates.congruence import Cong
from newclid.symbols.lines_registry import LineSymbol
from newclid.symbols.points_registry import Line
from newclid.symbols.symbols_registry import LineOrCircle, SymbolsRegistry


class Para(PredicateInterface):
    """para A B C D -
    Represent that the line AB is parallel to the line CD.
    """

    predicate_type: Literal[PredicateType.PARALLEL] = PredicateType.PARALLEL
    line1: Line
    line2: Line

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        return Cong.preparse(args)

    def check_numerical(self) -> bool:
        a, b = self.line1
        c, d = self.line2
        line1_angle = (b.num - a.num).angle() % np.pi
        line2_angle = (d.num - c.num).angle() % np.pi
        if (
            not close_enough(line2_angle, line1_angle)
            and not close_enough(line2_angle, line1_angle + np.pi)
            and not close_enough(line2_angle, line1_angle - np.pi)
        ):
            return False
        return True

    def symbols(self, symbols: SymbolsRegistry) -> tuple[LineOrCircle, ...]:
        # Create the lines that are parallel in the symbols graph
        parallels: list[LineSymbol] = []
        a, b = self.line1
        c, d = self.line2
        parallels.append(symbols.lines.line_thru_pair(a, b))
        parallels.append(symbols.lines.line_thru_pair(c, d))
        return tuple(parallels)

    def to_constructive(self, point: str) -> str:
        a, b = [p.name for p in self.line1]
        c, d = [p.name for p in self.line2]
        if point in [c, d]:
            a, b, c, d = c, d, a, b
        if point == b:
            a, b = b, a
        return f"on_pline {a} {b} {c} {d}"

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.line1 + self.line2)

    def __str__(self) -> str:
        a, b = self.line1
        c, d = self.line2
        return f"{a}{b} ∥ {c}{d}"


class NPara(NumericalPredicate):
    """npara A B C D -
    Represent that lines AB and CD are NOT parallel.

    It can only be numerically checked
    (angular coefficient of the equations of the lines are different).
    """

    predicate_type: Literal[PredicateType.N_PARALLEL] = PredicateType.N_PARALLEL

    line1: Line
    line2: Line

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        return Para.preparse(args)

    def check_numerical(self) -> bool:
        a, b = self.line1
        c, d = self.line2
        l1 = line_num_from_points(a.num, b.num)
        l2 = line_num_from_points(c.num, d.num)
        return not l1.is_parallel(l2)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.line1 + self.line2)

    def __str__(self) -> str:
        a, b = self.line1
        c, d = self.line2
        return f"{a}{b} ∦ {c}{d}"
