"""Helper functions for manipulating points when matching theorems for DD."""

from typing import Any, Generator

from newclid.combinatorics import memoized
from newclid.geometry import Line, Point


@memoized
def rotate_simtri(
    a: Point, b: Point, c: Point, x: Point, y: Point, z: Point
) -> Generator[tuple[Point, ...], None, None]:
    """Rotate points around for similar triangle predicates."""
    yield (z, y, x, c, b, a)
    for p in [
        (b, c, a, y, z, x),
        (c, a, b, z, x, y),
        (x, y, z, a, b, c),
        (y, z, x, b, c, a),
        (z, x, y, c, a, b),
    ]:
        yield p
        yield p[::-1]


@memoized
def rotate_contri(
    a: Point, b: Point, c: Point, x: Point, y: Point, z: Point
) -> Generator[tuple[Point, ...], None, None]:
    for p in [(b, a, c, y, x, z), (x, y, z, a, b, c), (y, x, z, b, a, c)]:
        yield p


def diff_point(line: Line, a: Point) -> Point:
    for x in line.neighbors(Point):
        if x != a:
            return x
    return None


def intersect1(set1: set[Any], set2: set[Any]) -> Any:
    for x in set1:
        if x in set2:
            return x
    return None
