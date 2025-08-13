from __future__ import annotations

from typing import Literal

from newclid.numerical.check import same_clock
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import NumericalPredicate
from newclid.symbols.points_registry import Triangle


class SameClock(NumericalPredicate):
    """sameclock a b c x y z -"""

    predicate_type: Literal[PredicateType.SAME_CLOCK] = PredicateType.SAME_CLOCK
    triangle1: Triangle
    triangle2: Triangle

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, c, x, y, z = args
        if a == b or b == c or a == c or x == y or y == z or x == z:
            return None
        group = min((a, b, c), (b, c, a), (c, a, b))
        groupr = min((a, c, b), (c, b, a), (b, a, c))
        group1 = min((x, y, z), (y, z, x), (z, x, y))
        group1r = min((x, z, y), (z, y, x), (y, x, z))
        return min(group + group1, group1 + group, groupr + group1r, group1r + groupr)

    def check_numerical(self) -> bool:
        a, b, c = self.triangle1
        x, y, z = self.triangle2
        return same_clock(a.num, b.num, c.num, x.num, y.num, z.num)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.triangle1 + self.triangle2)

    def __str__(self) -> str:
        a, b, c = self.triangle1
        x, y, z = self.triangle2
        return f"▲{a}{b}{c} has the same orientation as ▲{x}{y}{z}"
