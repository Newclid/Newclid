from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from newclid.numerical import close_enough
from newclid.numerical.geometries import circle_num_from_points_around
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Point

if TYPE_CHECKING:
    from newclid.proof_state import ProofState


class Cyclic(PredicateInterface):
    """cyclic A B C D -
    Represent that 4 (or more) points lie on the same circle."""

    predicate_type: Literal[PredicateType.CYCLIC] = PredicateType.CYCLIC

    points: tuple[Point, ...]

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        if len(set(args)) <= 3:
            return None
        return tuple(sorted(set(args)))

    def check_numerical(self) -> bool:
        p1, p2, p3 = self.points[:3]
        try:
            circle = circle_num_from_points_around([p1.num, p2.num, p3.num])
        except ValueError:
            return False
        return all(
            close_enough(circle.radius**2, circle.center.distance2(p.num))
            for p in self.points[3:]
        )

    def check(self, proof_state: ProofState) -> bool | None:
        return proof_state.symbols.circles.check_cyclic(self.points)

    def add(self, proof_state: ProofState) -> tuple[PredicateInterface, ...]:
        proof_state.symbols.circles.make_cyclic(self.points, justification=self)
        return ()

    def to_constructive(self, point: str) -> str:
        a, b, c = [x.name for x in self.points if x.name != point]
        return f"on_circum {point} {a} {b} {c}"

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.points)

    def __str__(self) -> str:
        return f"{''.join(str(p) for p in self.points)} are cyclic"
