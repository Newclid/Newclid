from __future__ import annotations

from typing import Literal, Optional

from newclid.numerical import close_enough
from newclid.numerical.check import same_clock
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.predicates.triangles_similar import two_triangles
from newclid.symbols.points_registry import Triangle


class ContriClock(PredicateInterface):
    """contri A B C P Q R -

    Represent that triangles ABC and PQR are congruent under orientation-preserving
    transformations taking A to P, B to Q and C to R.

    It is equivalent to the three eqangle and eqratio predicates
    on the corresponding angles and sides.
    """

    predicate_type: Literal[PredicateType.CONTRI_CLOCK] = PredicateType.CONTRI_CLOCK
    triangle1: Triangle
    triangle2: Triangle

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> Optional[tuple[PredicateArgument, ...]]:
        return two_triangles(*args)

    def check_numerical(self) -> bool:
        a, b, c = self.triangle1
        p, q, r = self.triangle2
        return (
            close_enough(a.num.distance(b.num), p.num.distance(q.num))
            and close_enough(a.num.distance(c.num), p.num.distance(r.num))
            and close_enough(b.num.distance(c.num), q.num.distance(r.num))
            and same_clock(a.num, b.num, c.num, p.num, q.num, r.num)
        )

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.triangle1 + self.triangle2)

    def __str__(self) -> str:
        a, b, c = self.triangle1
        p, q, r = self.triangle2
        return f"▲{a}{b}{c} ≡ ▲{p}{q}{r}"


class ContriReflect(PredicateInterface):
    """contrir A B C P Q R -

    Represent that triangles ABC and PQR are congruent under orientation-preserving
    transformations taking A to P, B to Q and C to R.

    It is equivalent to the three eqangle and eqratio predicates
    on the corresponding angles and sides.
    """

    predicate_type: Literal[PredicateType.CONTRI_REFLECT] = PredicateType.CONTRI_REFLECT
    triangle1: Triangle
    triangle2: Triangle

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        return two_triangles(*args)

    def check_numerical(self) -> bool:
        a, b, c = self.triangle1
        p, q, r = self.triangle2
        return (
            close_enough(a.num.distance(b.num), p.num.distance(q.num))
            and close_enough(a.num.distance(c.num), p.num.distance(r.num))
            and close_enough(b.num.distance(c.num), q.num.distance(r.num))
            and same_clock(a.num, b.num, c.num, p.num, r.num, q.num)
        )

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.triangle1 + self.triangle2)

    def __str__(self) -> str:
        a, b, c = self.triangle1
        p, q, r = self.triangle2
        return f"▲{a}{b}{c} ≡ ▲{p}{q}{r}"
