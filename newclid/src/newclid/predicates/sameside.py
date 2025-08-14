from __future__ import annotations

from typing import Literal

from newclid.numerical import sign
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import NumericalPredicate
from newclid.symbols.points_registry import Triangle


class SameSide(NumericalPredicate):
    """sameside a b c x y z

    Represent that a in the same kind of arc (smaller or larger) with respect to b-c as x is with respect to y-z (includes the degenerate case of the circle being a line).

    If a, b, c or x, y, z are not in the same circle/line, turns true if a is closer/further/at the same distance to the midpoint of b-c and, respectively, x is closer/further/at the same distance to the midpoint of y-z.

    Numerical only.
    """

    predicate_type: Literal[PredicateType.SAME_SIDE] = PredicateType.SAME_SIDE
    triangle1: Triangle
    triangle2: Triangle

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, c, x, y, z = args
        if a == b or b == c or a == c or x == y or y == z or x == z:
            return None
        p1 = min((a, b, c), (a, c, b))
        p2 = min((x, y, z), (x, z, y))
        return min(p1 + p2, p2 + p1)

    def check_numerical(self) -> bool:
        a, b, c = self.triangle1
        x, y, z = self.triangle2
        sa = sign((b.num - a.num).dot(c.num - a.num))
        sx = sign((y.num - x.num).dot(z.num - x.num))
        return sa == sx

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.triangle1 + self.triangle2)

    def __str__(self) -> str:
        a, b, c = self.triangle1
        x, y, z = self.triangle2
        return f"{a} is to the same side of {b}->{c} as {x} is to {y}->{z}"


class NSameSide(NumericalPredicate):
    """nsameside a b c x y z

    Represent that a is to the different side of b->c as x is to y->z.

    Numerical only.
    """

    predicate_type: Literal[PredicateType.N_SAME_SIDE] = PredicateType.N_SAME_SIDE
    triangle1: Triangle
    triangle2: Triangle

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        return SameSide.preparse(args)

    def check_numerical(self) -> bool:
        return not SameSide(
            triangle1=self.triangle1, triangle2=self.triangle2
        ).check_numerical()

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.triangle1 + self.triangle2)

    def __str__(self) -> str:
        a, b, c = self.triangle1
        x, y, z = self.triangle2
        return f"{a} is to the different side of {b}->{c} as {x} is to {y}->{z}"
