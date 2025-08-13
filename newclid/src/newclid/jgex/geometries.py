from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Sequence, Union

import numpy as np
from numpy.random import Generator
from pydantic import BaseModel

from newclid.jgex.errors import (
    InvalidIntersectError,
    JGEXConstructionError,
    PointTooCloseError,
)
from newclid.numerical import close_enough, nearly_zero, sign

LENGTH_UNIT = 1.0
"""Base unit for lengths. Here to avoid numerical precision issues if dealing with too little numbers."""


class JGEXPoint(BaseModel):
    """Numerical point."""

    x: float
    y: float

    def __add__(self, p: JGEXPoint) -> JGEXPoint:
        return JGEXPoint(x=self.x + p.x, y=self.y + p.y)

    def __sub__(self, p: JGEXPoint) -> JGEXPoint:
        return JGEXPoint(x=self.x - p.x, y=self.y - p.y)

    def __mul__(self, f: Any) -> JGEXPoint:
        f = float(f)
        return JGEXPoint(x=self.x * f, y=self.y * f)

    def __rmul__(self, f: Any) -> JGEXPoint:
        return self * float(f)

    def __truediv__(self, f: Any) -> JGEXPoint:
        f = float(f)
        return JGEXPoint(x=self.x / f, y=self.y / f)

    def __str__(self) -> str:
        return "PointNum({},{})".format(self.x, self.y)

    def __abs__(self) -> str:
        return np.sqrt(self.dot(self))

    def angle(self) -> float:
        return np.arctan2(self.y, self.x)

    def close_enough(self, point: JGEXPoint) -> bool:
        return close_enough(self.x, point.x) and close_enough(self.y, point.y)

    def distance(self, p: Union[JGEXPoint, JGEXLine, JGEXCircle]) -> float:
        return np.sqrt(self.distance2(p))

    def distance2(self, p: Union[JGEXPoint, JGEXLine, JGEXCircle]) -> float:
        if isinstance(p, JGEXLine):
            return p.distance(self)
        if isinstance(p, JGEXCircle):
            return (p.radius - self.distance(p.center)) ** 2
        dx = self.x - p.x
        dy = self.y - p.y
        dx2 = dx * dx
        dy2 = dy * dy
        dx2 = 0.0 if nearly_zero(dx2) else dx2
        dy2 = 0.0 if nearly_zero(dy2) else dy2
        return dx2 + dy2

    def rot90(self) -> JGEXPoint:
        return JGEXPoint(x=-self.y, y=self.x)

    def rotatea(self, ang: Any) -> JGEXPoint:
        sinb, cosb = np.sin(ang), np.cos(ang)
        return self.rotate(sinb, cosb)

    def rotate(self, sinb: Any, cosb: Any) -> JGEXPoint:
        x, y = self.x, self.y
        return JGEXPoint(x=x * cosb - y * sinb, y=x * sinb + y * cosb)

    def flip(self) -> JGEXPoint:
        return JGEXPoint(x=-self.x, y=self.y)

    def perpendicular_line(self, line: JGEXLine) -> JGEXLine:
        return line.perpendicular_line(self)

    def foot(self, line: Union[JGEXLine, JGEXCircle]) -> JGEXPoint:
        if isinstance(line, JGEXLine):
            perpendicular_line = line.perpendicular_line(self)
            return line_line_intersection(perpendicular_line, line)[0]
        else:
            c, r = line.center, line.radius
            return c + (self - c) * r / self.distance(c)

    def parallel_line(self, line: JGEXLine) -> JGEXLine:
        return line.parallel_line(self)

    def dot(self, other: JGEXPoint) -> float:
        res = self.x * other.x + self.y * other.y
        return 0 if nearly_zero(res) else res

    @classmethod
    def deduplicate(cls, points: Iterable[JGEXPoint]) -> list[JGEXPoint]:
        res: list[JGEXPoint] = []
        for p in points:
            if all(not r.close_enough(p) for r in res):
                res.append(p)
        return res

    def intersect(self, obj: JGEXGeometry) -> list[JGEXPoint]:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"JGEXPoint({self.x}, {self.y})"


class JGEXGeometry(ABC):
    @abstractmethod
    def sample_within(
        self, points: Sequence[JGEXPoint], *, trials: int = 5, rng: Generator
    ) -> JGEXPoint: ...


class JGEXLine(JGEXGeometry):
    """Numerical line."""

    def __init__(
        self,
        p1: Optional["JGEXPoint"] = None,
        p2: Optional["JGEXPoint"] = None,
        coefficients: Optional[tuple[float, float, float]] = None,
    ):
        a, b, c = None, None, None
        if coefficients:
            a, b, c = coefficients
        elif p1 and p2:
            if p1.close_enough(p2):
                raise PointTooCloseError(
                    f"Not able to determine the line by points {p1} and {p2} as they are too close (distance: {p1.distance(p2)})"
                )
            a, b, c = (
                p1.y - p2.y,
                p2.x - p1.x,
                p1.x * p2.y - p2.x * p1.y,
            )
        assert a is not None and b is not None and c is not None

        # Make sure a is always positive (or always negative for that matter)
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

    def __call__(self, p: JGEXPoint) -> float:
        a, b, c = self.coefficients
        res = p.x * a + p.y * b + c
        return 0 if nearly_zero(res) else res

    def parallel_line(self, p: JGEXPoint) -> JGEXLine:
        a, b, _ = self.coefficients
        return JGEXLine(coefficients=(a, b, -a * p.x - b * p.y))

    def perpendicular_line(self, p: JGEXPoint) -> JGEXLine:
        a, b, _ = self.coefficients
        return JGEXLine(p, p + JGEXPoint(x=a, y=b))

    def distance(self, p: JGEXPoint) -> float:
        return abs(self(p))

    def is_parallel(self, other: JGEXLine) -> bool:
        a, b, _ = self.coefficients
        x, y, _ = other.coefficients
        return close_enough(a * y, b * x)

    def is_perp(self, other: JGEXLine) -> bool:
        a, b, _ = self.coefficients
        x, y, _ = other.coefficients
        return close_enough(a * x, -b * y)

    def is_same(self, other: JGEXLine) -> bool:
        a, b, c = self.coefficients
        x, y, z = other.coefficients
        return close_enough(a * y, b * x) and close_enough(b * z, c * y)

    def point_at(
        self, x: Optional[float] = None, y: Optional[float] = None
    ) -> Optional[JGEXPoint]:
        """Infer the point on the line by its x and/or y coordinate(s)"""
        a, b, c = self.coefficients
        # ax + by + c = 0
        if x is None and y is not None:
            if not close_enough(a, 0):
                return JGEXPoint(x=(-c - b * y) / a, y=y)
            else:
                return None
        elif x is not None and y is None:
            if not close_enough(b, 0):
                return JGEXPoint(x=x, y=(-c - a * x) / b)
            else:
                return None
        elif x is not None and y is not None:
            if close_enough(a * x + b * y, -c):
                return JGEXPoint(x=x, y=y)
        return None

    def diff_side(self, p1: JGEXPoint, p2: JGEXPoint) -> bool:
        d1 = self(p1)
        d2 = self(p2)
        if nearly_zero(d1) or nearly_zero(d2):
            return False
        return d1 * d2 < 0

    def same_side(self, p1: JGEXPoint, p2: JGEXPoint) -> bool:
        d1 = self(p1)
        d2 = self(p2)
        if close_enough(d1, 0) or close_enough(d2, 0):
            return False
        return d1 * d2 > 0

    def sample_within(
        self, points: Sequence[JGEXPoint], *, trials: int = 5, rng: Generator
    ) -> JGEXPoint:
        """Sample a point on the line within the boundary of existing points."""
        center: JGEXPoint = sum(points, JGEXPoint(x=0.0, y=0.0)) / len(points)  # type: ignore
        radius = max([p.distance(center) for p in points])

        if close_enough(center.distance(self), radius):
            center = center.foot(self)
        a, b = line_circle_intersection(
            self, JGEXCircle(center.foot(self), radius), expected_points=2
        )
        result = None
        best = -1.0
        for _ in range(trials):
            rand = rng.uniform(0.0, 1.0)
            x = a + (b - a) * rand
            mind = min([x.distance(p) for p in points])
            if mind > best:
                best = mind
                result = x

        if result is None:
            raise JGEXConstructionError(
                "Could not sample a point on line within the boundary of points"
            )
        return result

    def angle(self) -> float:
        if nearly_zero(self.coefficients[1]):
            return np.pi / 2
        phead = self.point_at(x=1)
        ptail = self.point_at(x=0)
        if phead is None or ptail is None:
            raise ValueError("Cannot compute the angle if no head or tail.")
        angle = (phead - ptail).angle() % np.pi
        if close_enough(angle, np.pi):
            return 0.0
        return angle

    def angle_to(self, other: JGEXLine) -> float:
        return (self.angle() - other.angle()) % np.pi

    def __repr__(self) -> str:
        return f"JGEXLine({self.coefficients[0]}, {self.coefficients[1]}, {self.coefficients[2]})"


class JGEXCircle(JGEXGeometry):
    """Numerical circle."""

    def __init__(
        self,
        center: Optional[JGEXPoint] = None,
        radius: Optional[float] = None,
        p1: Optional[JGEXPoint] = None,
        p2: Optional[JGEXPoint] = None,
        p3: Optional[JGEXPoint] = None,
    ):
        if center:
            self.center = center
        else:
            if not (p1 and p2 and p3):
                raise ValueError("Circle without center need p1 p2 p3")
            l12 = perpendicular_bisector(p1, p2)
            l23 = perpendicular_bisector(p2, p3)
            (self.center,) = line_line_intersection(l12, l23)

        self.a, self.b = self.center.x, self.center.y
        self.points = [p for p in (p1, p2, p3) if p is not None]

        if not radius:
            p = p1 or p2 or p3
            if p is None:
                raise ValueError("Circle needs radius or p1 or p2 or p3")
            self.r2: float = (self.a - p.x) ** 2 + (self.b - p.y) ** 2
            self.radius: float = np.sqrt(self.r2)
        else:
            self.radius = radius
            self.r2 = radius * radius

    def sample_within(
        self, points: Sequence[JGEXPoint], *, trials: int = 5, rng: Generator
    ) -> JGEXPoint:
        """Sample a point on the circle."""
        random_angle = rng.uniform(0.0, 2.0) * np.pi
        sampled_point = self.center + self.radius * JGEXPoint(
            x=np.cos(random_angle), y=np.sin(random_angle)
        )
        return sampled_point

    def __repr__(self) -> str:
        return f"JGEXCircle(c={self.center}, r={self.radius}, points={self.points}])"


def perpendicular_bisector(p1: JGEXPoint, p2: JGEXPoint) -> JGEXLine:
    midpoint = (p1 + p2) * 0.5
    return JGEXLine(midpoint, midpoint + JGEXPoint(x=p2.y - p1.y, y=p1.x - p2.x))


def solve_quad(a: float, b: float, c: float) -> tuple[float, ...]:
    """Solve a x^2 + bx + c = 0."""
    if nearly_zero(a):
        return () if nearly_zero(b) else (-c / b,)
    a = 2 * a
    d = b * b - 2 * a * c
    sd = sign(d)
    if sd == -1:
        return ()
    if sd == 0:
        d = 0.0
    y = np.sqrt(d)
    if nearly_zero(y):
        return (-b / a,)
    return (-b - y) / a, (-b + y) / a


def intersect(a: JGEXGeometry, b: JGEXGeometry):
    if isinstance(a, JGEXCircle):
        if isinstance(b, JGEXCircle):
            return circle_circle_intersection(a, b)
        if isinstance(b, JGEXLine):
            return line_circle_intersection(b, a)
    if isinstance(a, JGEXLine):
        if isinstance(b, JGEXCircle):
            return line_circle_intersection(a, b)
        if isinstance(b, JGEXLine):
            return line_line_intersection(a, b, ensure_point=False)
    raise NotImplementedError


def circle_circle_intersection(
    c1: JGEXCircle, c2: JGEXCircle, expected_points: int | None = None
) -> tuple[JGEXPoint, ...]:
    """Returns a pair of Points as intersections of c1 and c2."""
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1
    x0, y0, r0 = c1.a, c1.b, c1.radius
    x1, y1, r1 = c2.a, c2.b, c2.radius

    d: float = (x1 - x0) ** 2 + (y1 - y0) ** 2
    if nearly_zero(d):
        raise InvalidIntersectError(
            f"Circles {c1} and {c2} have the same center and thus cannot intersect"
        )
    d = np.sqrt(d)

    if not (r0 + r1 >= d and abs(r0 - r1) <= d):
        raise InvalidIntersectError(f"Circles {c1} and {c2} do intersect")

    a = (r0**2 - r1**2 + d**2) / (2 * d)
    h = r0**2 - a**2
    biu: JGEXPoint = (c2.center - c1.center) / d
    qiu = biu.rot90()
    p = c1.center + a * biu
    if nearly_zero(h):
        if expected_points is not None and expected_points != 1:
            raise InvalidIntersectError(
                f"Expected {expected_points} intersections between circles {c1} and {c2}, but they are tangent"
            )
        return (p,)

    if expected_points is not None and expected_points != 2:
        raise InvalidIntersectError(
            f"Expected {expected_points} intersections between circles, but they are crossing"
        )

    qiu = np.sqrt(h) * qiu

    return (p + qiu, p - qiu)


def line_circle_intersection(
    line: JGEXLine, circle: JGEXCircle, expected_points: int = 1
) -> tuple[JGEXPoint, ...]:
    a, b, c = line.coefficients
    r = circle.radius
    center = circle.center
    p, q = center.x, center.y
    if nearly_zero(b):
        x = -c / a
        x_p = x - p
        x_p2 = x_p * x_p
        points = tuple(
            JGEXPoint(x=x, y=y1) for y1 in solve_quad(1, -2 * q, q * q + x_p2 - r * r)
        )
    elif close_enough(a, 0):
        y = -c / b
        y_q = y - q
        y_q2 = y_q * y_q
        points = tuple(
            JGEXPoint(x=x1, y=y) for x1 in solve_quad(1, -2 * p, p * p + y_q2 - r * r)
        )

    else:
        c_ap = c + a * p
        a2 = a * a
        points = tuple(
            JGEXPoint(x=-(b * y1 + c) / a, y=y1)
            for y1 in solve_quad(
                a2 + b * b, 2 * (b * c_ap - a2 * q), c_ap * c_ap + a2 * (q * q - r * r)
            )
        )
    if len(points) < expected_points:
        raise InvalidIntersectError(
            f"Expected at least {expected_points} intersections between line and circle, got {len(points)}"
        )
    return points


def line_line_intersection(
    line_1: JGEXLine, line_2: JGEXLine, ensure_point: bool = True
) -> tuple[JGEXPoint, ...]:
    a1, b1, c1 = line_1.coefficients
    a2, b2, c2 = line_2.coefficients
    # a1x + b1y + c1 = 0
    # a2x + b2y + c2 = 0
    d = a1 * b2 - a2 * b1
    if nearly_zero(d):
        if ensure_point:
            raise InvalidIntersectError(
                f"Expected 1 intersection between lines, got {d}"
            )
        return ()
    return (JGEXPoint(x=(c2 * b1 - c1 * b2) / d, y=(c1 * a2 - c2 * a1) / d),)


def reduce_intersection(
    objs: Sequence[JGEXGeometry],
    existing_points: Sequence[JGEXPoint],
    rng: Generator,
) -> list[JGEXPoint]:
    """Reduce intersecting objects into one new point."""
    if all(isinstance(o, JGEXPoint) for o in objs):
        return list(objs)  # type: ignore

    if len(objs) == 1:
        obj = objs[0]
        return [obj.sample_within(existing_points, rng=rng)]

    if len(objs) == 2:
        u, v = objs
        intersections: tuple[JGEXPoint, ...] = intersect(u, v)
        shuffled_intersections = np.array(intersections)  # pyright: ignore
        rng.shuffle(shuffled_intersections)  # pyright: ignore
        shuffled_intersections: tuple[JGEXPoint, ...] = tuple(shuffled_intersections)  # type: ignore
        for p in shuffled_intersections:
            is_valid = all(not p.close_enough(x) for x in existing_points)
            if is_valid:
                return [p]
        raise InvalidIntersectError(
            f"Could not reduce {objs} to a single new point, intersections: {intersections}, existing points: {existing_points}"
        )

    raise NotImplementedError
