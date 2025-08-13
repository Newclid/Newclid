from __future__ import annotations

from typing import Iterator, Literal

from pydantic import BaseModel

from newclid.justifications._index import JustificationError, JustificationType
from newclid.numerical.geometries import LineNum, line_num_from_points
from newclid.predicates.collinearity import Coll
from newclid.symbols._index import SymbolType
from newclid.symbols.merging_symbols import (
    SymbolMergeHistory,
    merge_symbols,
    representent_of,
)
from newclid.symbols.points_registry import Point


class LineSymbol(BaseModel):
    """
    The LineSymbol class represents a line identified by a coll predicate in the symbolic registry.
    Its attributes are:
    - points: the set of Point objects known to belong to the line
    - num: the LineNum object that contains the numerical parameters of the line
    - justification: a Coll predicate that justifies the existence of this line in the symbols registry
    - symbol_type: a constant indicating that this is a line symbol (SymbolType.LINE).
    """

    points: set[Point]
    num: LineNum
    justification: Coll | None  # TODO: Should not be able to be None
    symbol_type: Literal[SymbolType.LINE] = SymbolType.LINE

    def __str__(self) -> str:
        sorted_point_names = sorted(p.name for p in self.points)
        return "Line(" + "-".join(sorted_point_names) + ")"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(str(self))


class LinesRegistry:
    def __init__(self) -> None:
        self._lines: list[LineSymbol] = []
        self._merge_history: dict[LineSymbol, SymbolMergeHistory[LineSymbol]] = {}

    def create_line_thru_points(
        self, points: set[Point], because: Coll | None = None
    ) -> LineSymbol:
        if len(points) < 2:
            raise ValueError("Line needs at least two points")
        p1, p2 = list(points)[:2]
        line_num = line_num_from_points(p1.num, p2.num)
        line = LineSymbol(justification=because, points=points, num=line_num)
        self._lines.append(line)
        self._merge_history[line] = SymbolMergeHistory(symbol=line)
        return line

    def line_thru_pair(self, p1: Point, p2: Point) -> LineSymbol:
        for line in self._lines:
            if {p1, p2} <= line.points:
                for line1 in self._merge_history[line].fellows:
                    if {p1, p2} == line1.points:
                        return line1
                other_line = self.create_line_thru_points({p1, p2}, because=None)
                assert line.justification
                merge_symbols(
                    self._merge_history[line],
                    [self._merge_history[other_line]],
                    self._lines,
                )
                return other_line
        return self.create_line_thru_points({p1, p2}, because=None)

    def representent(self, line: LineSymbol) -> LineSymbol:
        return representent_of(self._merge_history[line]).symbol

    def line_containing(self, pnames: set[Point]) -> LineSymbol | None:
        for line in self._lines:
            if pnames <= line.points:
                return line
        return None

    def check_collinear(
        self,
        points: tuple[Point, ...],
    ) -> bool:
        s = set(points)
        for line in self._lines:
            if s <= line.points:
                return True
        return False

    def make_collinear(
        self, points: tuple[Point, ...], justification: Coll
    ) -> tuple[LineSymbol, list[LineSymbol]]:
        points_set = set(points)
        merged: list[LineSymbol] = []
        for other_line in self._lines:
            if points_set <= other_line.points:
                # Already belong to the an existing line
                return other_line, []
            if len(points_set & other_line.points) >= 2:
                merged.append(other_line)
                points_set.update(other_line.points)

        line = self.create_line_thru_points(points_set, because=justification)
        merge_symbols(
            self._merge_history[line],
            [self._merge_history[line] for line in merged],
            self._lines,
        )
        return line, merged

    def why_colllinear(self, coll: Coll) -> LineMerge:
        points: tuple[Point, ...] = coll.points
        s = set(points)
        for line in self._lines:
            if not s <= line.points:
                continue
            line_target = line
            for _target in self._merge_history[line].fellows:
                if s <= _target.points and len(_target.points) < len(
                    line_target.points
                ):
                    line_target = _target
            if not line_target.justification:
                raise ValueError(
                    f"Line {line_target} was merged in the symbols graph without justification."
                )
            return LineMerge(
                predicate=coll,
                line=line_target,
                direct_justification=line_target.justification,
            )
        raise JustificationError("Could not justify why the points would be collinear")

    def get_all_points_on_line_and_equivalent_lines(
        self, line: LineSymbol
    ) -> set[Point]:
        points: set[Point] = set()
        for equivalent_line in self._merge_history[line].fellows:
            for pt in equivalent_line.points:
                points.add(pt)
        return points

    def __iter__(self) -> Iterator[LineSymbol]:
        return iter(self._lines)


class LineMerge(BaseModel):
    predicate: Coll
    """The predicate that is justified by the symbols graph merge."""
    line: LineSymbol
    """The line symbol that was merged."""
    direct_justification: Coll
    """The previous predicate that directly justifies the merge that has the predicate as a consequence."""

    dependency_type: Literal[JustificationType.LINE_MERGE] = (
        JustificationType.LINE_MERGE
    )
