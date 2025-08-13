from __future__ import annotations

from typing import Literal

import numpy as np

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Segment
from newclid.symbols.symbols_registry import LineOrCircle, SymbolsRegistry
from newclid.tools import reshape

AngleArgs = tuple[
    PredicateArgument, PredicateArgument, PredicateArgument, PredicateArgument
]


class EqAngle(PredicateInterface):
    """eqangle AB CD EF GH -
    Represent that one can rigidly move the crossing of lines AB and CD
    to get on top of the crossing of EF and GH, respectively (no reflections allowed).

    In particular, eqangle AB CD CD AB is only true if AB is perpendicular or parallel to CD.
    """

    predicate_type: Literal[PredicateType.EQUAL_ANGLES] = PredicateType.EQUAL_ANGLES
    angle1: tuple[Segment, Segment]
    angle2: tuple[Segment, Segment]

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        groups: list[AngleArgs] = []
        groups1: list[AngleArgs] = []
        if len(args) % 4:
            return None
        for a, b, c, d in reshape(args, 4):
            if a == b or c == d:
                return None
            a, b = sorted((a, b))
            c, d = sorted((c, d))
            groups.append((a, b, c, d))
            groups1.append((c, d, a, b))
        return sum(min(sorted(groups), sorted(groups1)), ())

    def check_numerical(self) -> bool:
        (a, b), (c, d) = self.angle1
        (e, f), (g, h) = self.angle2

        angle1 = ((d.num - c.num).angle() - (b.num - a.num).angle()) % np.pi
        angle2 = ((h.num - g.num).angle() - (f.num - e.num).angle()) % np.pi

        if (
            not close_enough(angle1, angle2)
            and not close_enough(angle1, angle2 + np.pi)
            and not close_enough(angle1, angle2 - np.pi)
        ):
            return False
        return True

    def symbols(self, symbols: SymbolsRegistry) -> tuple[LineOrCircle, ...]:
        (a, b), (c, d) = self.angle1
        l1 = symbols.lines.line_thru_pair(a, b)
        l2 = symbols.lines.line_thru_pair(c, d)
        (e, f), (g, h) = self.angle2
        l3 = symbols.lines.line_thru_pair(e, f)
        l4 = symbols.lines.line_thru_pair(g, h)
        return (l1, l2, l3, l4)

    @staticmethod
    def to_constructive(point: str, args: tuple[str, ...]) -> str:
        a, b, c, d, e, f = args

        if point in [d, e, f]:
            a, b, c, d, e, f = d, e, f, a, b, c

        x, b, y, c, d = b, c, e, d, f
        if point == b:
            a, b, c, d = b, a, d, c

        if point == d and x == y:  # x p x b = x c x p
            return f"angle_bisector {point} {b} {x} {c}"

        if point == x:
            return f"eqangle3 {x} {a} {b} {y} {c} {d}"

        return f"on_aline {a} {x} {b} {c} {y} {d}"

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(
            PredicateArgument(p.name)
            for ((a, b), (c, d)) in [self.angle1, self.angle2]
            for p in (a, b, c, d)
        )

    def __str__(self) -> str:
        return " = ".join(
            f"∠({a}{b},{c}{d})" for ((a, b), (c, d)) in [self.angle1, self.angle2]
        )
