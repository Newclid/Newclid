from __future__ import annotations

from newclid.numerical import ATOM
from newclid.numerical.geometries import PointNum


def same_clock(
    a: PointNum, b: PointNum, c: PointNum, d: PointNum, e: PointNum, f: PointNum
) -> bool:
    """
    a, b, c; d, e, f are of the same clock and they are not colinear
    """
    clock_left = clock(a, b, c)
    clock_right = clock(d, e, f)
    return (clock_left > ATOM and clock_right > ATOM) or (
        clock_left < -ATOM and clock_right < -ATOM
    )


def clock(a: PointNum, b: PointNum, c: PointNum):
    ab = b - a
    ac = c - a
    return ab.x * ac.y - ab.y * ac.x
