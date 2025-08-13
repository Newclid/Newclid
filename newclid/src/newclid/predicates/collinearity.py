from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

from newclid.numerical.geometries import line_num_from_points
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import NumericalPredicate, PredicateInterface
from newclid.symbols.points_registry import Point

if TYPE_CHECKING:
    from newclid.proof_state import ProofState
    from newclid.symbols.symbols_registry import LineOrCircle, SymbolsRegistry


class Coll(PredicateInterface):
    """coll A B C ... -
    Represent that the 3 (or more) points in the arguments are collinear."""

    predicate_type: Literal[PredicateType.COLLINEAR] = PredicateType.COLLINEAR

    points: tuple[Point, ...]

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        if len(set(args)) <= 2:
            return None
        return tuple(sorted(set(args)))

    def check_numerical(self) -> bool:
        a, b = self.points[:2]
        line = line_num_from_points(a.num, b.num)
        return all(line.point_at(p.num.x, p.num.y) is not None for p in self.points[2:])

    def add(self, proof_state: ProofState) -> tuple[PredicateInterface, ...]:
        proof_state.symbols.lines.make_collinear(self.points, justification=self)
        return ()

    def check(self, proof_state: ProofState) -> bool | None:
        return proof_state.symbols.lines.check_collinear(self.points)

    def symbols(self, symbols: SymbolsRegistry) -> tuple[LineOrCircle, ...]:
        _rep, merged = symbols.lines.make_collinear(self.points, justification=self)
        return tuple(merged)

    def to_constructive(self, point: str) -> str:
        a, b, c = [p.name for p in self.points if p.name != point]
        if point == b:
            a, b = b, a
        if point == c:
            a, b, c = c, a, b
        return f"on_line {a} {b} {c}"

    def __str__(self) -> str:
        return f"{', '.join(str(p) for p in self.points)} are collinear"

    def __hash__(self) -> int:
        return hash(str(self))

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.points)


class NColl(NumericalPredicate):
    """ncoll A B C ... -
    Represent that any of the 3 (or mo}re) points is not aligned with the others.

    Numerical only.
    """

    predicate_type: Literal[PredicateType.N_COLLINEAR] = PredicateType.N_COLLINEAR

    points: tuple[Point, ...]

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> Optional[tuple[PredicateArgument, ...]]:
        return Coll.preparse(args)

    def check_numerical(self) -> bool:
        return not Coll(points=self.points).check_numerical()

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in self.points)

    def __str__(self) -> str:
        return f"{', '.join(str(p) for p in self.points)} are not collinear"
