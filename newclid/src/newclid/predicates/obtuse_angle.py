from __future__ import annotations

from typing import Literal

from newclid.numerical import ATOM
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import NumericalPredicate
from newclid.symbols.points_registry import Point


class ObtuseAngle(NumericalPredicate):
    """obtuse_angle a b c

    Represents that the angle `a b c` is an obtuse angle.
    If `a`, `b`, `c` are collinear, this predicate represents that `b` is between `a` and `c`.

    Numerical only.
    """

    predicate_type: Literal[PredicateType.OBTUSE_ANGLE] = PredicateType.OBTUSE_ANGLE

    head1: Point
    corner: Point
    head2: Point

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, c = args
        if a == b or b == c or a == c:
            return None
        (a, c) = sorted((a, c))
        return (a, b, c)

    def check_numerical(self) -> bool:
        ray_1 = self.head1.num - self.corner.num
        ray_2 = self.head2.num - self.corner.num
        return ray_1.dot(ray_2) < -ATOM

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(
            PredicateArgument(p.name) for p in (self.head1, self.corner, self.head2)
        )

    def __str__(self) -> str:
        return f"∠({self.head2}{self.corner}{self.head1}) is an obtuse angle"
