from __future__ import annotations

from typing import Literal

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Segment


class Cong(PredicateInterface):
    """cong A B C D -
    Represent that segments AB and CD are congruent."""

    predicate_type: Literal[PredicateType.CONGRUENT] = PredicateType.CONGRUENT
    segment1: Segment
    segment2: Segment

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        segs: list[tuple[PredicateArgument, PredicateArgument]] = []
        if len(args) % 2 != 0:
            return None
        for a, b in zip(args[::2], args[1::2]):
            if a > b:
                a, b = b, a
            if a == b:
                return None
            segs.append((a, b))
        segs.sort()
        segs = list(set(segs))
        points: list[PredicateArgument] = []
        if len(segs) == 0:
            return None

        elif len(segs) == 1:
            a, b = segs[0]
            points.append(a)
            points.append(b)
            points.append(a)
            points.append(b)

        else:
            for a, b in segs:
                points.append(a)
                points.append(b)
        return tuple(points)

    def check_numerical(self) -> bool:
        a, b = self.segment1
        l1 = a.num.distance2(b.num)
        c, d = self.segment2
        l2 = c.num.distance2(d.num)
        return close_enough(l1, l2)

    def to_constructive(self, point: str) -> str:
        a, b, c, d = self.segment1 + self.segment2
        if point in [c.name, d.name]:
            a, b, c, d = c, d, a, b
        if point == b.name:
            a, b = b, a
        if point == d.name:
            c, d = d, c
        if a.name == c.name and a.name == point:
            return f"on_bline {a.name} {b.name} {d.name}"
        if b.name in [c.name, d.name]:
            if b.name == d.name:
                c, d = d, c
            return f"on_circle {a.name} {b.name} {d.name}"
        return f"eqdistance {a.name} {b.name} {c.name} {d.name}"

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.segment1 + self.segment2)

    def __str__(self) -> str:
        a, b = self.segment1
        c, d = self.segment2
        return f"{a}{b} = {c}{d}"
