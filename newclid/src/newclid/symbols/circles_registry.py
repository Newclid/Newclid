from __future__ import annotations

from typing import Iterator, Literal

from pydantic import BaseModel

from newclid.justifications._index import JustificationError, JustificationType
from newclid.numerical.geometries import CircleNum, circle_num_from_points_around
from newclid.predicates.cyclic import Cyclic
from newclid.symbols._index import SymbolType
from newclid.symbols.merging_symbols import SymbolMergeHistory, merge_symbols
from newclid.symbols.points_registry import Point


class CircleSymbol(BaseModel):
    """
    The CircleSymbol class represents a circle identitfied by a cyclic predicate in the symbolic registry. It has the following attributes:
    - points: the set of points known to lie on the circle.
    - justification: a Cyclic predicate that justifies the existence of this circle.
    - num: a CircleNum that represents the numerical parameter of the circle.
    - symbol_type: a constant indicating that this is a CircleSymbol (SymbolType.CIRCLE).
    """

    points: set[Point]
    justification: Cyclic
    num: CircleNum
    symbol_type: Literal[SymbolType.CIRCLE] = SymbolType.CIRCLE

    def __str__(self) -> str:
        sorted_points_names = sorted(p.name for p in self.points)
        return "Circle(" + "-".join(sorted_points_names) + ")"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(str(self))


class CirclesRegistry:
    def __init__(self) -> None:
        self._circles: list[CircleSymbol] = []
        self._merge_history: dict[CircleSymbol, SymbolMergeHistory[CircleSymbol]] = {}

    def create_circle_thru_points(
        self, points: set[Point], because: Cyclic
    ) -> CircleSymbol:
        circle_num = circle_num_from_points_around([p.num for p in points])
        circle = CircleSymbol(justification=because, points=points, num=circle_num)
        self._circles.append(circle)
        self._merge_history[circle] = SymbolMergeHistory(symbol=circle)
        return circle

    def circle_containing(self, pnames: set[Point]) -> CircleSymbol | None:
        for circle in self._circles:
            if pnames <= circle.points:
                return circle
        return None

    def check_cyclic(self, points: tuple[Point, ...]) -> bool:
        s = set(points)
        for c in self._circles:
            if s <= c.points:
                return True
        return False

    def make_cyclic(self, points: tuple[Point, ...], justification: Cyclic) -> None:
        points_set = set(points)
        merged: list[CircleSymbol] = []
        for other_circle in self._circles:
            if points_set <= other_circle.points:
                # Already belong to the an existing circle
                return
            if len(points_set & other_circle.points) >= 3:
                merged.append(other_circle)
                points_set.update(other_circle.points)

        circle_to_merge = self.create_circle_thru_points(
            points_set, because=justification
        )
        merge_symbols(
            self._merge_history[circle_to_merge],
            [self._merge_history[merged_circle] for merged_circle in merged],
            self._circles,
        )

    def why_cyclic(self, cyclic: Cyclic) -> CircleMerge:
        points_set = set(cyclic.points)
        for circle in self._circles:
            if not points_set <= circle.points:
                continue
            circle_target = circle
            for _target in self._merge_history[circle].fellows:
                if points_set <= _target.points and len(_target.points) < len(
                    circle_target.points
                ):
                    circle_target = _target
            return CircleMerge(
                predicate=cyclic,
                circle=circle_target,
                direct_justification=circle_target.justification,
            )
        raise JustificationError("Could not justify why the points would be concyclic")

    def __iter__(self) -> Iterator[CircleSymbol]:
        return iter(self._circles)


class CircleMerge(BaseModel):
    predicate: Cyclic
    """The predicate that is justified by the symbols graph merge."""
    circle: CircleSymbol
    """The circle symbol that was merged."""
    direct_justification: Cyclic
    """The previous predicate that directly justifies the merge that has the predicate as a consequence."""

    dependency_type: Literal[JustificationType.CIRCLE_MERGE] = (
        JustificationType.CIRCLE_MERGE
    )

    def __hash__(self) -> int:
        return hash(self.predicate)
