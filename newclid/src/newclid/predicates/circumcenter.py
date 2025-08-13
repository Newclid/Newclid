from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from newclid.numerical import close_enough
from newclid.numerical.geometries import CircleNum
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.predicates.congruence import Cong
from newclid.predicates.cyclic import Cyclic
from newclid.symbols.points_registry import Point

if TYPE_CHECKING:
    from newclid.proof_state import ProofState


class Circumcenter(PredicateInterface):
    """circle O A B C -
    Represent that O is the center of the circle through A, B, and C
    (circumcenter of triangle ABC).

    Can be equivalent to cong O A O B and cong O A O C,
    and equivalent pairs of congruences.
    """

    predicate_type: Literal[PredicateType.CIRCUMCENTER] = PredicateType.CIRCUMCENTER

    center: Point
    points: tuple[Point, ...]

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        if len(set(args)) <= 3:
            return None
        return (args[0],) + tuple(sorted(set(args[1:])))

    def check_numerical(self) -> bool:
        radius = self.center.num.distance(self.points[0].num)
        circle = CircleNum(center=self.center.num, radius=radius)
        return all(
            close_enough(circle.radius, circle.center.distance(p.num))
            for p in self.points[1:]
        )

    def check(self, proof_state: ProofState) -> bool | None:
        o = self.center
        p0 = self.points[0]
        for p1 in self.points[1:]:
            cong = Cong(segment1=(o, p0), segment2=(o, p1))
            if not proof_state.check(cong):
                return False
        return True

    def add(self, proof_state: ProofState) -> tuple[PredicateInterface, ...]:
        o = self.center
        p0 = self.points[0]
        consequences: list[PredicateInterface] = []
        for p1 in self.points[1:]:
            cong = Cong(segment1=(o, p0), segment2=(o, p1))
            consequences.append(cong)
        if len(self.points) > 3:
            cyclic = Cyclic(points=self.points[1:])
            consequences.append(cyclic)
        return tuple(consequences)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        str_tokens = [self.center.name] + [p.name for p in self.points]
        return tuple(PredicateArgument(t) for t in str_tokens)

    def __str__(self) -> str:
        points_str = "".join(str(p) for p in self.points)
        return f"{self.center} is the circumcenter of the circle ●{points_str}"
