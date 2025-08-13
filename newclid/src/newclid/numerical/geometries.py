from __future__ import annotations

from typing import Any, Iterable, Optional, Self, Union

import numpy as np
from pydantic import BaseModel, model_validator

from newclid.numerical import close_enough, nearly_zero, sign


class PointNum(BaseModel):
    """
    This class contains the geometric coordinates of a point, and the functions needed to manipulate points as 2D vectors on the plane.

    Its attributes are the x and y coordinates of the point, which are floats.

    It contains the methods:

    - angle: returns the angle of the point with respect to the x-axis.
    - close_enough: checks if two points are close enough to be considered equal.
    - distance: computes the distance between the point and another point, line, or circle.
    - distance2: computes the squared distance between the point and another point, line, or circle.
    - rot90: returns a new point rotated 90 degrees counterclockwise.
    - rotatea: rotates the point by a given angle in radians.
    - rotate: rotates the point by given sine and cosine values.
    - flip: reflects the point across the y-axis.
    - perpendicular_line: returns a line perpendicular to a given line through this point.
    - foot: computes the closest point from this point on a line or circle.
    - parallel_line: returns a line parallel to a given line through this point.
    - dot: computes the dot product with another point as a vector.
    - deduplicate: class method to remove duplicate points from an iterable of points.
    """

    x: float
    y: float

    def __add__(self, p: PointNum) -> PointNum:
        return PointNum(x=self.x + p.x, y=self.y + p.y)

    def __sub__(self, p: PointNum) -> PointNum:
        return PointNum(x=self.x - p.x, y=self.y - p.y)

    def __mul__(self, f: Any) -> PointNum:
        f = float(f)
        return PointNum(x=self.x * f, y=self.y * f)

    def __rmul__(self, f: Any) -> PointNum:
        return self * float(f)

    def __truediv__(self, f: Any) -> PointNum:
        f = float(f)
        return PointNum(x=self.x / f, y=self.y / f)

    def __str__(self) -> str:
        return "PointNum({},{})".format(self.x, self.y)

    def __abs__(self) -> str:
        return np.sqrt(self.dot(self))

    def angle(self) -> float:
        return np.arctan2(self.y, self.x)

    def close_enough(self, point: PointNum) -> bool:
        return close_enough(self.x, point.x) and close_enough(self.y, point.y)

    def distance(self, p: Union[PointNum, LineNum, CircleNum]) -> float:
        return np.sqrt(self.distance2(p))

    def distance2(self, p: Union[PointNum, LineNum, CircleNum]) -> float:
        if isinstance(p, LineNum):
            return p.distance(self)
        if isinstance(p, CircleNum):
            return (p.radius - self.distance(p.center)) ** 2
        dx = self.x - p.x
        dy = self.y - p.y
        dx2 = dx * dx
        dy2 = dy * dy
        return dx2 + dy2

    def rot90(self) -> PointNum:
        return PointNum(x=-self.y, y=self.x)

    def rotatea(self, ang: Any) -> PointNum:
        sinb, cosb = np.sin(ang), np.cos(ang)
        return self.rotate(sinb, cosb)

    def rotate(self, sinb: Any, cosb: Any) -> PointNum:
        x, y = self.x, self.y
        return PointNum(x=x * cosb - y * sinb, y=x * sinb + y * cosb)

    def flip(self) -> PointNum:
        return PointNum(x=-self.x, y=self.y)

    def perpendicular_line(self, line: LineNum) -> LineNum:
        return line.perpendicular_line(self)

    def foot(self, line: Union[LineNum, CircleNum]) -> PointNum:
        if isinstance(line, LineNum):
            perpendicular_line = line.perpendicular_line(self)
            intersect = line_line_intersection(
                perpendicular_line, line, ensure_point=True
            )
            return intersect[0]
        else:
            c, r = line.center, line.radius
            return c + (self - c) * r / self.distance(c)

    def parallel_line(self, line: LineNum) -> LineNum:
        return line.parallel_line(self)

    def dot(self, other: PointNum) -> float:
        res = self.x * other.x + self.y * other.y
        return 0 if nearly_zero(res) else res

    @classmethod
    def deduplicate(cls, points: Iterable[PointNum]) -> list[PointNum]:
        res: list[PointNum] = []
        for p in points:
            if all(not r.close_enough(p) for r in res):
                res.append(p)
        return res

    def __repr__(self) -> str:
        return f"PointNum({self.x}, {self.y})"


def line_num_from_points(p1: PointNum, p2: PointNum) -> LineNum:
    a, b, c = p1.y - p2.y, p2.x - p1.x, p1.x * p2.y - p2.x * p1.y
    return LineNum(coefficients=(a, b, c))


class LineNum(BaseModel):
    """
    This class contains the numerical parameters of a line defined by the equation ax + by + c = 0.

    Its only attribute is a tuple of three floats representing the coefficients (a, b, c) of the line equation.

    It contains the methods for geometric manipulations of the line:

    - parallel_line: returns a line parallel to this line through a given point.
    - perpendicular_line: returns a line perpendicular to this line through a given point.
    - distance: computes the distance from a point to the line.
    - is_parallel: checks if this line is parallel to another line.
    - is_perp: checks if this line is perpendicular to another line.
    - is_same: checks if this line is the same as another line.
    - point_at: infers if a point is on the line by its x and/or y coordinate(s).
    - diff_side: checks if two points are on different sides of the line.
    - same_side: checks if two points are on the same side of the line.
    - angle: computes the angle of the line with respect to the x-axis.
    - angle_to: computes the angle between this line and another line.
    """

    coefficients: tuple[float, float, float]  # pyright: ignore

    @model_validator(mode="after")
    def validate_coefficients(self) -> Self:
        a, b, c = self.coefficients
        # Make sure a is always positive
        # With a == 0, Assuming a = +epsilon > 0
        # Then b such that ax + by = 0 with y>0 should be negative.
        sa = sign(a)
        sb = sign(b)
        if sa == -1 or sa == 0 and sb == 1:
            a, b, c = -a, -b, -c
        if sa == 0:
            a = 0.0
        if sb == 0:
            b = 0.0
        if nearly_zero(c):
            c = 0.0

        d: float = np.sqrt(a**2 + b**2)
        self.coefficients: tuple[float, float, float] = a / d, b / d, c / d
        return self

    def __call__(self, p: PointNum) -> float:
        a, b, c = self.coefficients
        res = p.x * a + p.y * b + c
        return 0 if nearly_zero(res) else res

    def parallel_line(self, p: PointNum) -> LineNum:
        a, b, _ = self.coefficients
        return LineNum(coefficients=(a, b, -a * p.x - b * p.y))

    def perpendicular_line(self, p: PointNum) -> LineNum:
        a, b, _ = self.coefficients
        return line_num_from_points(p, p + PointNum(x=a, y=b))

    def distance(self, p: PointNum) -> float:
        return abs(self(p))

    def is_parallel(self, other: LineNum) -> bool:
        a, b, _ = self.coefficients
        x, y, _ = other.coefficients
        return close_enough(a * y, b * x)

    def is_perp(self, other: LineNum) -> bool:
        a, b, _ = self.coefficients
        x, y, _ = other.coefficients
        return close_enough(a * x, -b * y)

    def is_same(self, other: LineNum) -> bool:
        a, b, c = self.coefficients
        x, y, z = other.coefficients
        return close_enough(a * y, b * x) and close_enough(b * z, c * y)

    def point_at(
        self, x: Optional[float] = None, y: Optional[float] = None
    ) -> Optional[PointNum]:
        """Infer the point on the line by its x and/or y coordinate(s)"""
        a, b, c = self.coefficients
        # ax + by + c = 0
        if x is None and y is not None:
            if not close_enough(a, 0):
                return PointNum(x=(-c - b * y) / a, y=y)
            else:
                return None
        elif x is not None and y is None:
            if not close_enough(b, 0):
                return PointNum(x=x, y=(-c - a * x) / b)
            else:
                return None
        elif x is not None and y is not None:
            if close_enough(a * x + b * y, -c):
                return PointNum(x=x, y=y)
        return None

    def diff_side(self, p1: PointNum, p2: PointNum) -> bool:
        d1 = self(p1)
        d2 = self(p2)
        if nearly_zero(d1) or nearly_zero(d2):
            return False
        return d1 * d2 < 0

    def same_side(self, p1: PointNum, p2: PointNum) -> bool:
        d1 = self(p1)
        d2 = self(p2)
        if close_enough(d1, 0) or close_enough(d2, 0):
            return False
        return d1 * d2 > 0

    def angle(self) -> float:
        if nearly_zero(self.coefficients[1]):
            return np.pi / 2
        phead = self.point_at(x=1)
        ptail = self.point_at(x=0)
        if phead is None or ptail is None:
            raise TypeError("Cannot compute the angle if no head or tail.")
        angle = (phead - ptail).angle() % np.pi
        if close_enough(angle, np.pi):
            return 0.0
        return angle

    def angle_to(self, other: LineNum) -> float:
        return (self.angle() - other.angle()) % np.pi

    def __repr__(self) -> str:
        return f"LineNum({self.coefficients[0]}, {self.coefficients[1]}, {self.coefficients[2]})"


def circle_num_from_points_around(points: list[PointNum]) -> CircleNum:
    if len(points) < 3:
        raise ValueError("Circle needs at least three points")
    p1, p2, p3 = points[:3]
    l12 = _perpendicular_bisector(p1, p2)
    l23 = _perpendicular_bisector(p2, p3)
    (center,) = line_line_intersection(l12, l23)
    return circle_num_from_center_and_point(center, p1)


def circle_num_from_center_and_point(center: PointNum, point: PointNum) -> CircleNum:
    return CircleNum(center=center, radius=center.distance(point))


class CircleNum(BaseModel):
    """
    This class contains the numerical parameters of a circle.

    Its attributes are the center of the circle (a PointNum) and the radius (a float).
    """

    center: PointNum
    radius: float

    def __repr__(self) -> str:
        return f"CircleNum(c={self.center}, r={self.radius})"


def _perpendicular_bisector(p1: PointNum, p2: PointNum) -> LineNum:
    midpoint = (p1 + p2) * 0.5
    bisector_point = midpoint + PointNum(x=p2.y - p1.y, y=p1.x - p2.x)
    return line_num_from_points(midpoint, bisector_point)


def line_line_intersection(
    line_1: LineNum, line_2: LineNum, ensure_point: bool = False
) -> tuple[PointNum, ...]:
    a1, b1, c1 = line_1.coefficients
    a2, b2, c2 = line_2.coefficients
    # a1x + b1y + c1 = 0
    # a2x + b2y + c2 = 0
    d = a1 * b2 - a2 * b1
    if nearly_zero(d):
        if ensure_point:
            raise ValueError(f"Expected 1 intersection between lines, got {d}")
        return ()
    return (PointNum(x=(c2 * b1 - c1 * b2) / d, y=(c1 * a2 - c2 * a1) / d),)
