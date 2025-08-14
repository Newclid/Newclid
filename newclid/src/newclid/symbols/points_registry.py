from __future__ import annotations

from typing import Collection, Iterator, TypeAlias

from pydantic import BaseModel

from newclid.numerical.geometries import PointNum
from newclid.predicate_types import PredicateArgument


class Point(BaseModel):
    """The Point class is the symbolic representation of a geometric point."""

    name: PredicateArgument
    num: PointNum
    """The numerical representation of the point."""

    def __str__(self) -> str:
        p = self.name[0].upper()
        for c in self.name[1:]:
            if c.isdigit():
                p += chr(ord("₀") + ord(c) - ord("0"))
            else:
                p += f"_{c}"
        return p

    def __hash__(self) -> int:
        return hash(str(self))


class PointsRegisty:
    """Registry of points, used in the proof state to manage existing points."""

    def __init__(self) -> None:
        self.name_to_point: dict[PredicateArgument, Point] = {}

    def add_point(self, point: Point) -> None:
        self.name_to_point[point.name] = point

    def names2points(self, pnames: Collection[PredicateArgument]) -> list[Point]:
        """Return Point objects given names."""
        points: list[Point] = []
        for name in pnames:
            if name not in self.name_to_point:
                raise ValueError(f"Cannot find point {name} in graph")
            points.append(self.name_to_point[name])
        return points

    def __iter__(self) -> Iterator[Point]:
        return iter(self.name_to_point.values())


"""
Here we list the different types corresponding to geometric objects that are arguments of predicates. They are all composed of instances of the Point class. They are:

- Segment: a 2-tuple of Points representing a segment with the points are extremities.
- Ratio: a 2-tuple of Segments representing a ratio between the lengths of two segments.
- Line: a 2-tuple of Points representing a line through them.
- Angle: a 2-tuple of Lines representing the angle formed by them.
- Triangle: a 3-tuple of Points representing a triangle with the points as vertices.
"""

Segment: TypeAlias = tuple[Point, Point]
Ratio: TypeAlias = tuple[Segment, Segment]
Line: TypeAlias = tuple[Point, Point]
Angle: TypeAlias = tuple[Line, Line]
Triangle: TypeAlias = tuple[Point, Point, Point]
