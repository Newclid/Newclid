from __future__ import annotations

from typing import Literal, Optional, TypeVar

from newclid.numerical import close_enough
from newclid.numerical.check import same_clock
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Triangle

T = TypeVar("T", bound=str)


def two_triangles(
    a: T, b: T, c: T, p: T, q: T, r: T
) -> Optional[tuple[T, T, T, T, T, T]]:
    if a == b or a == c or b == c or p == q or p == r or q == r:
        return None
    if a == p and b == q and c == r:
        return None

    (a0, p0), (b0, q0), (c0, r0) = sorted(((a, p), (b, q), (c, r)))
    (a1, p1), (b1, q1), (c1, r1) = sorted(((p, a), (q, b), (r, c)))
    return min((a0, b0, c0, p0, q0, r0), (a1, b1, c1, p1, q1, r1))


class SimtriClock(PredicateInterface):
    """simtri A B C P Q R -

    Represent that triangles ABC and PQR are similar under orientation-preserving
    transformations taking A to P, B to Q and C to R.

    It is equivalent to the three eqangle and eqratio predicates
    on the corresponding angles and sides.
    """

    predicate_type: Literal[PredicateType.SIMTRI_CLOCK] = PredicateType.SIMTRI_CLOCK
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

        ab = a.num.distance(b.num)
        ac = a.num.distance(c.num)
        bc = b.num.distance(c.num)
        pq = p.num.distance(q.num)
        pr = p.num.distance(r.num)
        qr = q.num.distance(r.num)
        return (
            close_enough(ab * pr, ac * pq)
            and close_enough(bc * pr, ac * qr)
            and same_clock(a.num, b.num, c.num, p.num, q.num, r.num)
        )

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.triangle1 + self.triangle2)

    def __str__(self) -> str:
        a, b, c = self.triangle1
        p, q, r = self.triangle2
        return f"▲{a}{b}{c} ≅ ▲{p}{q}{r}"


class SimtriReflect(PredicateInterface):
    """simtrir A B C P Q R -

    Represent that triangles ABC and PQR are similar under orientation-preserving
    transformations taking A to P, B to Q and C to R.

    It is equivalent to the three eqangle and eqratio predicates
    on the corresponding angles and sides.
    """

    predicate_type: Literal[PredicateType.SIMTRI_REFLECT] = PredicateType.SIMTRI_REFLECT
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
        ab = a.num.distance(b.num)
        ac = a.num.distance(c.num)
        bc = b.num.distance(c.num)
        pq = p.num.distance(q.num)
        pr = p.num.distance(r.num)
        qr = q.num.distance(r.num)
        return (
            close_enough(ab * pr, ac * pq)
            and close_enough(bc * pr, ac * qr)
            and same_clock(a.num, b.num, c.num, p.num, r.num, q.num)
        )

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.triangle1 + self.triangle2)

    def __str__(self) -> str:
        a, b, c = self.triangle1
        p, q, r = self.triangle2
        return f"▲{a}{b}{c} ≅ ▲{p}{q}{r}"
