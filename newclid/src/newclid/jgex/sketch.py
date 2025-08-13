from __future__ import annotations

import logging
from fractions import Fraction
from typing import Any, Union

import numpy as np
from numpy.random import Generator

from newclid.jgex.angles import ang_between, ang_of
from newclid.jgex.geometries import (
    LENGTH_UNIT,
    JGEXCircle,
    JGEXGeometry,
    JGEXLine,
    JGEXPoint,
    circle_circle_intersection,
    line_circle_intersection,
    line_line_intersection,
)
from newclid.numerical import close_enough, nearly_zero
from newclid.tools import str_to_fraction

LOGGER = logging.getLogger(__name__)


def sketch(
    name: str, args: tuple[Union[JGEXPoint, str], ...], rng: Generator
) -> list[JGEXGeometry]:
    fun = globals()["sketch_" + name]
    res = fun(args, rng=rng)
    if isinstance(res, list) or isinstance(res, tuple):
        return list(res)  # type: ignore
    return [res]


def sketch_function_name(name: str) -> str:
    return name.split("sketch_")[1]


def sketch_aline(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXLine:
    """Sketch the construction aline."""
    A, B, C, D, E = args
    ab = A - B
    cb = C - B
    de = D - E

    ang_ab = np.arctan2(ab.y, ab.x)
    ang_bc = np.arctan2(cb.y, cb.x)
    ang_de = np.arctan2(de.y, de.x)

    ang_ex = ang_de + ang_bc - ang_ab
    X = E + LENGTH_UNIT * JGEXPoint(x=np.cos(ang_ex), y=np.sin(ang_ex))
    return JGEXLine(E, X)


def sketch_aline0(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXLine:
    """Sketch the construction aline0."""
    A, B, C, D, E, F, G = args
    ab = A - B
    cd = C - D
    ef = E - F

    ang_ab = np.arctan2(ab.y, ab.x)
    ang_cd = np.arctan2(cd.y, cd.x)
    ang_ef = np.arctan2(ef.y, ef.x)

    ang_ex = ang_ef + ang_cd - ang_ab
    X = G + LENGTH_UNIT * JGEXPoint(x=np.cos(ang_ex), y=np.sin(ang_ex))
    return JGEXLine(G, X)


def sketch_acircle(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXCircle:
    a, b, c, d, f = args
    de = sketch_aline((c, a, b, f, d))
    fe = sketch_aline((a, c, b, d, f))
    (e,) = line_line_intersection(de, fe)
    return JGEXCircle(p1=d, p2=e, p3=f)


def sketch_amirror(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint], **kwargs: Any
) -> JGEXLine:
    """Sketch the angle mirror."""
    A, B, C = args
    ab = A - B
    cb = C - B

    dab = A.distance(B)
    ang_ab = np.arctan2(ab.y / dab, ab.x / dab)
    dcb = C.distance(B)
    ang_bc = np.arctan2(cb.y / dcb, cb.x / dcb)

    ang_bx = 2 * ang_bc - ang_ab
    X = B + LENGTH_UNIT * JGEXPoint(x=np.cos(ang_bx), y=np.sin(ang_bx))
    return JGEXLine(B, X)


def sketch_bisect(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint], **kwargs: Any
) -> JGEXLine:
    a, b, c = args
    ab = a.distance(b)
    bc = b.distance(c)
    x = b + (c - b) * (ab / bc)
    m = (a + x) / 2
    return JGEXLine(b, m)


def sketch_exbisect(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint], **kwargs: Any
) -> JGEXLine:
    _, b, _ = args
    return sketch_bisect(args).perpendicular_line(b)


def sketch_bline(args: tuple[JGEXPoint, JGEXPoint], **kwargs: Any) -> JGEXLine:
    a, b = args
    m = (a + b) / 2
    return m.perpendicular_line(JGEXLine(a, b))


def sketch_dia(args: tuple[JGEXPoint, JGEXPoint], **kwargs: Any) -> JGEXCircle:
    a, b = args
    return JGEXCircle((a + b) / 2, p1=a)


def sketch_tangent(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint], **kwargs: Any
) -> tuple[JGEXPoint, ...]:
    a, o, b = args
    dia = sketch_dia((a, o))
    return circle_circle_intersection(JGEXCircle(o, p1=b), dia)


def sketch_circle(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint], **kwargs: Any
) -> JGEXCircle:
    a, b, c = args
    return JGEXCircle(center=a, radius=b.distance(c))


def sketch_cc_tangent(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint, JGEXPoint], **kwargs: Any
) -> tuple[JGEXPoint, ...]:
    """Sketch external tangents to two circles."""
    o, a, w, b = args
    ra, rb = o.distance(a), w.distance(b)

    ow = JGEXLine(o, w)

    if close_enough(ra, rb):
        oo = ow.perpendicular_line(o)
        oa = JGEXCircle(o, ra)
        x, z = line_circle_intersection(oo, oa, expected_points=2)
        y = x + w - o
        t = z + w - o
        return x, y, z, t

    swap = rb > ra
    if swap:
        o, a, w, b = w, b, o, a
        ra, rb = rb, ra

    if close_enough(o.distance(w), abs(rb - ra)):
        LOGGER.debug(
            "The circles are internally tangent. Try another definition of a tangent line."
        )
    elif o.distance(w) < abs(rb - ra):
        LOGGER.debug("One circle is inside the other and there are no tangents.")

    oa = JGEXCircle(o, ra)
    q = o + (w - o) * ra / (ra - rb)

    x, z = circle_circle_intersection(sketch_dia((o, q)), oa, expected_points=2)
    y = w.foot(JGEXLine(x, q))
    i = w.foot(JGEXLine(z, q))

    if swap:
        x, y, z, i = y, x, i, z

    return x, y, z, i


def sketch_e5128(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> tuple[JGEXPoint, JGEXPoint]:
    a, b, c, d = args

    g = (a + b) / 2
    de = JGEXLine(d, g)

    e, f = line_circle_intersection(de, JGEXCircle(c, p1=b), expected_points=2)

    if e.distance(d) < f.distance(d):
        e = f
    return e, g


def random_rfss(*points: JGEXPoint, rng: Generator) -> list[JGEXPoint]:
    """Random rotate-flip-scale-shift a JGEXPoint cloud."""
    # center point cloud.
    average = sum(points, JGEXPoint(x=0.0, y=0.0)) / len(points)
    points = tuple(p - average for p in points)

    # rotate
    ang = rng.uniform(0.0, 2 * np.pi)
    sin, cos = np.sin(ang), np.cos(ang)
    # scale and shift
    scale = rng.uniform(0.5, 2.0)
    shift = LENGTH_UNIT * JGEXPoint(x=rng.uniform(-1, 1), y=rng.uniform(-1, 1))
    points = tuple(p.rotate(sin, cos) * scale + shift for p in points)

    # randomly flip
    if rng.random() < 0.5:
        points = tuple(p.flip() for p in points)

    return list(points)


def head_from(tail: JGEXPoint, ang: float, length: float = LENGTH_UNIT) -> JGEXPoint:
    vector = JGEXPoint(x=np.cos(ang) * length, y=np.sin(ang) * length)
    return tail + vector


def sketch_eq_quadrangle(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    """Sketch quadrangle with two equal opposite sides."""
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=1.0, y=0.0)

    length = LENGTH_UNIT * rng.uniform(0.5, 2.0)
    ang = rng.uniform(np.pi / 3, np.pi * 2 / 3)
    d = head_from(a, ang, length)

    ang = ang_of(b, d)
    ang = rng.uniform(ang / 10, ang / 9)
    c = head_from(b, ang, length)
    a, b, c, d = random_rfss(a, b, c, d, rng=rng)
    return a, b, c, d


def sketch_iso_trapezoid(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=1.0, y=0.0)
    rel_lenght = rng.uniform(0.5, 2.0)
    rel_height = rng.uniform(0.5, 2.0)
    c = LENGTH_UNIT * JGEXPoint(x=0.5 + rel_lenght / 2.0, y=rel_height)
    d = LENGTH_UNIT * JGEXPoint(x=0.5 - rel_lenght / 2.0, y=rel_height)
    a, b, c, d = random_rfss(a, b, c, d, rng=rng)
    return a, b, c, d


def sketch_eqangle2(args: tuple[JGEXPoint, ...], rng: Generator) -> JGEXPoint:
    """Sketch the def eqangle2."""
    a, b, c = args

    ba = b.distance(a)
    bc = b.distance(c)
    length = ba * ba / bc

    if rng.uniform(0.0, 1.0) < 0.5:
        be = min(length, bc)
        be = rng.uniform(be * 0.1, be * 0.9)
    else:
        be = max(length, bc)
        be = rng.uniform(be * 1.1, be * 1.5)

    e = b + (c - b) * (be / bc)
    y = b + (a - b) * (be / length)
    return line_line_intersection(JGEXLine(c, y), JGEXLine(a, e))[0]


def sketch_eqangle3(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXCircle:
    a, b, d, e, f = args
    de = d.distance(e)
    ef = e.distance(f)
    ab = b.distance(a)
    ang_ax = ang_of(a, b) + ang_between(e, f, d)
    x = head_from(a, ang_ax, length=de / ef * ab)
    return JGEXCircle(p1=a, p2=b, p3=x)


def sketch_eqdia_quadrangle(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    """Sketch quadrangle with two equal diagonals."""
    rel_x = rng.uniform(0.3, 0.7)
    rel_y = rng.uniform(0.3, 0.7)
    a = LENGTH_UNIT * JGEXPoint(x=-rel_x, y=0.0)
    c = LENGTH_UNIT * JGEXPoint(x=1 - rel_x, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=0.0, y=-rel_y)
    d = LENGTH_UNIT * JGEXPoint(x=0.0, y=1 - rel_y)

    ang = rng.uniform(-0.25 * np.pi, 0.25 * np.pi)
    sin, cos = np.sin(ang), np.cos(ang)
    b = b.rotate(sin, cos)
    d = d.rotate(sin, cos)
    a, b, c, d = random_rfss(a, b, c, d, rng=rng)
    return a, b, c, d


def random_points(n: int, rng: Generator) -> list[JGEXPoint]:
    return [
        LENGTH_UNIT * JGEXPoint(x=rng.uniform(-1, 1), y=rng.uniform(-1, 1))
        for _ in range(n)
    ]


def sketch_free(args: tuple[JGEXPoint, ...], rng: Generator) -> JGEXPoint:
    return random_points(1, rng)[0]


def sketch_isos(args: tuple[JGEXPoint, ...], rng: Generator) -> tuple[JGEXPoint, ...]:
    rel_base = rng.uniform(0.5, 1.5)
    rel_height = rng.uniform(0.5, 1.5)

    b = LENGTH_UNIT * JGEXPoint(x=-rel_base / 2, y=0.0)
    c = LENGTH_UNIT * JGEXPoint(x=rel_base / 2, y=0.0)
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=rel_height)
    a, b, c = random_rfss(a, b, c, rng=rng)
    return a, b, c


def sketch_line(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXLine:
    a, b = args
    return JGEXLine(a, b)


def sketch_cyclic(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXCircle:
    a, b, c = args
    return JGEXCircle(p1=a, p2=b, p3=c)


def sketch_midp(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXPoint:
    a, b = args
    return (a + b) / 2


def sketch_pentagon(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    points = [LENGTH_UNIT * JGEXPoint(x=1.0, y=0.0)]
    ang = 0.0

    for i in range(4):
        ang += (2 * np.pi - ang) / (5 - i) * rng.uniform(0.5, 1.5)
        point = LENGTH_UNIT * JGEXPoint(x=np.cos(ang), y=np.sin(ang))
        points.append(point)

    a, b, c, d, e = points
    a, b, c, d, e = random_rfss(a, b, c, d, e, rng=rng)
    return a, b, c, d, e


def sketch_pline(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXLine:
    a, b, c = args
    return a.parallel_line(JGEXLine(b, c))


def sketch_pmirror(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXPoint:
    a, b = args
    return b * 2 - a


def sketch_quadrangle(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    """Sketch a random quadrangle."""
    rel_x = rng.uniform(0.3, 0.7)
    a = LENGTH_UNIT * JGEXPoint(x=-rel_x, y=0.0)
    c = LENGTH_UNIT * JGEXPoint(x=1 - rel_x, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=0.0, y=-rng.uniform(0.25, 0.75))
    d = LENGTH_UNIT * JGEXPoint(x=0.0, y=rng.uniform(0.25, 0.75))

    ang = rng.uniform(-0.25 * np.pi, 0.25 * np.pi)
    sin, cos = np.sin(ang), np.cos(ang)
    b = b.rotate(sin, cos)
    d = d.rotate(sin, cos)
    a, b, c, d = random_rfss(a, b, c, d, rng=rng)
    return a, b, c, d


def sketch_r_trapezoid(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=1.0)
    d = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=rng.uniform(0.5, 1.5), y=1.0)
    c = LENGTH_UNIT * JGEXPoint(x=rng.uniform(0.5, 1.5), y=0.0)
    a, b, c, d = random_rfss(a, b, c, d, rng=rng)
    return a, b, c, d


def sketch_r_triangle(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=0.0, y=rng.uniform(0.5, 2.0))
    c = LENGTH_UNIT * JGEXPoint(x=rng.uniform(0.5, 2.0), y=0.0)
    a, b, c = random_rfss(a, b, c, rng=rng)
    return a, b, c


def sketch_rectangle(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=0.0, y=1.0)
    rel_lenght = rng.uniform(0.5, 2.0)
    c = LENGTH_UNIT * JGEXPoint(x=rel_lenght, y=1.0)
    d = LENGTH_UNIT * JGEXPoint(x=rel_lenght, y=0.0)
    a, b, c, d = random_rfss(a, b, c, d, rng=rng)
    return a, b, c, d


def sketch_reflect(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXPoint:
    a, b, c = args
    m = a.foot(JGEXLine(b, c))
    return m * 2 - a


def sketch_risos(args: tuple[JGEXPoint, ...], rng: Generator) -> tuple[JGEXPoint, ...]:
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=0.0, y=1.0)
    c = LENGTH_UNIT * JGEXPoint(x=1.0, y=0.0)
    a, b, c = random_rfss(a, b, c, rng=rng)
    return a, b, c


def sketch_rotaten90(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXPoint:
    a, b = args
    ang = -np.pi / 2
    return a + (b - a).rotate(np.sin(ang), np.cos(ang))


def sketch_rotatep90(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXPoint:
    a, b = args
    ang = np.pi / 2
    return a + (b - a).rotate(np.sin(ang), np.cos(ang))


def sketch_s_angle(args: tuple[JGEXPoint, JGEXPoint, str], **kwargs: Any) -> JGEXLine:
    a, b, angle = args
    f = str_to_fraction(angle)
    ang = float(f) * np.pi
    x = b + (a - b).rotatea(ang)
    return JGEXLine(b, x)


def sketch_aconst(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint, str], **kwargs: Any
) -> JGEXLine:
    a, b, c, angle = args
    f = str_to_fraction(angle)
    ang = float(f) * np.pi
    x = c + (a - b).rotatea(ang)
    return JGEXLine(c, x)


def sketch_segment(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, JGEXPoint]:
    a, b = random_points(2, rng)
    return a, b


def sketch_shift(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXPoint:
    a, b, c = args
    return c + (b - a)


def sketch_square(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> tuple[JGEXPoint, JGEXPoint]:
    a, b = args
    c = b + (a - b).rotatea(-np.pi / 2)
    d = a + (b - a).rotatea(np.pi / 2)
    return c, d


def sketch_isquare(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=1.0, y=0.0)
    c = LENGTH_UNIT * JGEXPoint(x=1.0, y=1.0)
    d = LENGTH_UNIT * JGEXPoint(x=0.0, y=1.0)
    a, b, c, d = random_rfss(a, b, c, d, rng=rng)
    return a, b, c, d


def sketch_tline(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXLine:
    a, b, c = args
    return a.perpendicular_line(JGEXLine(b, c))


def sketch_trapezoid(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    d = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    c = LENGTH_UNIT * JGEXPoint(x=1.0, y=0.0)

    base = LENGTH_UNIT * rng.uniform(0.5, 2.0)
    height = LENGTH_UNIT * rng.uniform(0.5, 2.0)
    a = JGEXPoint(x=LENGTH_UNIT * rng.uniform(-0.5, 1.5), y=height)
    b = JGEXPoint(x=a.x + base, y=height)
    a, b, c, d = random_rfss(a, b, c, d, rng=rng)
    return a, b, c, d


def sketch_triangle(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, JGEXPoint, JGEXPoint]:
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=1.0, y=0.0)
    ac = LENGTH_UNIT * rng.uniform(0.5, 2.0)
    ang = rng.uniform(0.2, 0.8) * np.pi
    c = head_from(a, ang, ac)
    a, b, c = random_rfss(a, b, c, rng=rng)
    return a, b, c


def sketch_triangle12(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, JGEXPoint, JGEXPoint]:
    b = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    c = LENGTH_UNIT * JGEXPoint(x=rng.uniform(1.5, 2.5), y=0.0)

    circle_1 = JGEXCircle(b, LENGTH_UNIT)
    circle_2 = JGEXCircle(c, 2.0 * LENGTH_UNIT)
    a, _ = circle_circle_intersection(circle_1, circle_2, expected_points=2)
    a, b, c = random_rfss(a, b, c, rng=rng)
    return a, b, c


def sketch_trisect(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> tuple[JGEXPoint, JGEXPoint]:
    """Sketch two trisectors of an angle."""
    a, b, c = args
    ang1 = ang_of(b, a)
    ang2 = ang_of(b, c)

    swap = 0
    if ang1 > ang2:
        ang1, ang2 = ang2, ang1
        swap += 1

    if ang2 - ang1 > np.pi:
        ang1, ang2 = ang2, ang1 + 2 * np.pi
        swap += 1

    angx = ang1 + (ang2 - ang1) / 3
    angy = ang2 - (ang2 - ang1) / 3

    x = b + LENGTH_UNIT * JGEXPoint(x=np.cos(angx), y=np.sin(angx))
    y = b + LENGTH_UNIT * JGEXPoint(x=np.cos(angy), y=np.sin(angy))

    ac = JGEXLine(a, c)
    (x,) = line_line_intersection(JGEXLine(b, x), ac)
    (y,) = line_line_intersection(JGEXLine(b, y), ac)

    if swap == 1:
        return y, x
    return x, y


def sketch_trisegment(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> tuple[JGEXPoint, JGEXPoint]:
    a, b = args
    x, y = a + (b - a) * (1.0 / 3), a + (b - a) * (2.0 / 3)
    return x, y


def sketch_ieq_triangle(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    a = LENGTH_UNIT * JGEXPoint(x=0.0, y=0.0)
    b = LENGTH_UNIT * JGEXPoint(x=1.0, y=0.0)

    c, _ = circle_circle_intersection(
        JGEXCircle(a, p1=b), JGEXCircle(b, p1=a), expected_points=2
    )
    a, b, c = random_rfss(a, b, c, rng=rng)
    return a, b, c


def sketch_incenter2(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> tuple[JGEXPoint, JGEXPoint, JGEXPoint, JGEXPoint]:
    a, b, c = args
    l1 = sketch_bisect((b, a, c))
    l2 = sketch_bisect((a, b, c))
    (i,) = line_line_intersection(l1, l2)
    x = i.foot(JGEXLine(b, c))
    y = i.foot(JGEXLine(c, a))
    z = i.foot(JGEXLine(a, b))
    return x, y, z, i


def sketch_excenter2(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> tuple[JGEXPoint, JGEXPoint, JGEXPoint, JGEXPoint]:
    a, b, c = args
    l1 = sketch_bisect((b, a, c))
    l2 = sketch_exbisect((a, b, c))
    (i,) = line_line_intersection(l1, l2)
    x = i.foot(JGEXLine(b, c))
    y = i.foot(JGEXLine(c, a))
    z = i.foot(JGEXLine(a, b))
    return x, y, z, i


def sketch_centroid(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> tuple[JGEXPoint, JGEXPoint, JGEXPoint, JGEXPoint]:
    a, b, c = args
    x = (b + c) / 2
    y = (c + a) / 2
    z = (a + b) / 2
    (i,) = line_line_intersection(JGEXLine(a, x), JGEXLine(b, y))
    return x, y, z, i


def sketch_ninepoints(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> tuple[JGEXPoint, JGEXPoint, JGEXPoint, JGEXPoint]:
    a, b, c = args
    x = (b + c) / 2
    y = (c + a) / 2
    z = (a + b) / 2
    return x, y, z, JGEXCircle(p1=x, p2=y, p3=z).center


def sketch_2l1c(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> tuple[JGEXPoint, JGEXPoint, JGEXPoint, JGEXPoint]:
    """Sketch a circle touching two lines and another circle."""
    a, b, c, p = args
    bc, ac = JGEXLine(b, c), JGEXLine(a, c)
    circle = JGEXCircle(p, p1=a)

    d, d_ = line_circle_intersection(
        p.perpendicular_line(bc), circle, expected_points=2
    )
    if bc.diff_side(d_, a):
        d = d_

    e, e_ = line_circle_intersection(
        p.perpendicular_line(ac), circle, expected_points=2
    )
    if ac.diff_side(e_, b):
        e = e_

    df = d.perpendicular_line(JGEXLine(p, d))
    ef = e.perpendicular_line(JGEXLine(p, e))
    (f,) = line_line_intersection(df, ef)

    g, g_ = line_circle_intersection(JGEXLine(c, f), circle, expected_points=2)
    if bc.same_side(g_, a):
        g = g_

    b_ = c + (b - c) / b.distance(c)
    a_ = c + (a - c) / a.distance(c)
    m = (a_ + b_) / 2
    (x,) = line_line_intersection(JGEXLine(c, m), JGEXLine(p, g))
    return x.foot(ac), x.foot(bc), g, x


def sketch_3peq(args: tuple[JGEXPoint, ...], rng: Generator) -> tuple[JGEXPoint, ...]:
    a, b, c = args
    ab, _, ca = JGEXLine(a, b), JGEXLine(b, c), JGEXLine(c, a)

    z = b + (c - b) * rng.uniform(-0.5, 1.5)

    z_ = z * 2 - c
    ca_parallel_line = z_.parallel_line(ca)
    (x,) = line_line_intersection(ca_parallel_line, ab)
    y = z * 2 - x
    return x, y, z


# NEW FUNCTIONS FOR NEW DEFINITIONS ---- V. S.


def sketch_isosvertex(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXLine:
    b, c = args
    m = (b + c) / 2.0

    return m.perpendicular_line(JGEXLine(b, c))


def sketch_eqratio(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXCircle:
    A, B, C, D, E, F, G = args

    dab = A.distance(B)
    dcd = C.distance(D)
    d_ef = E.distance(F)

    dgx = d_ef * dcd / dab
    return JGEXCircle(center=G, radius=dgx)


def sketch_rconst(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint, str], **kwargs: Any
) -> JGEXCircle:
    """Sketches point x such that ab/cx=r"""
    A, B, C, r = args
    dab = A.distance(B)
    length = float(dab / float(str_to_fraction(r)))
    return JGEXCircle(center=C, radius=length)


def sketch_eqratio6(
    args: tuple[JGEXPoint, ...], **kwargs: Any
) -> Union[JGEXCircle, JGEXLine]:
    """Sketches a point x such that ax/cx=ef/gh"""
    A, C, E, F, G, H = args
    d_ef = E.distance(F)
    dgh = G.distance(H)

    if dgh == d_ef:
        M = (A + C) * 0.5
        return M.perpendicular_line(JGEXLine(A, C))

    else:
        ratio = d_ef / dgh
        extremum_1 = (1 / (1 - ratio)) * (A - ratio * C)
        extremum_2 = (1 / (1 + ratio)) * (ratio * C + A)
        center = (extremum_1 + extremum_2) / 2
        radius = extremum_1.distance(extremum_2) / 2
        return JGEXCircle(center=center, radius=radius)


def sketch_lconst(args: tuple[JGEXPoint, str], **kwargs: Any) -> JGEXCircle:
    """Sketches point x such that x in at lenght l of point a"""
    a, length = args
    return JGEXCircle(center=a, radius=float(str_to_fraction(length)))


def sketch_rconst2(
    args: tuple[JGEXPoint, JGEXPoint, str], **kwargs: Any
) -> Union[JGEXCircle, JGEXLine]:
    """Sketches point x such that ax/bx=r"""
    A, B, r = args
    ratio = float(str_to_fraction(r))

    if ratio == float(Fraction(1, 1)):
        M = (A + B) / 2
        return M.perpendicular_line(JGEXLine(A, B))

    extremum_1 = (1 / (1 - ratio)) * (A - ratio * B)  # pyright: ignore
    extremum_2 = (1 / (1 + ratio)) * (ratio * B + A)
    center = (extremum_1 + extremum_2) / 2
    radius = extremum_1.distance(extremum_2) / 2
    return JGEXCircle(center=center, radius=radius)


def sketch_between(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, JGEXPoint, JGEXPoint]:
    """Sketches a segment ab and a point c between them."""
    a, b = random_points(2, rng)
    c = a + (b - a) * rng.uniform(0.0, 1.0)
    return c, a, b


def sketch_between_bound(
    args: tuple[JGEXPoint, JGEXPoint], rng: Generator
) -> JGEXPoint:
    """Sketches a point x between a and b."""
    a, b = args
    return a + (b - a) * rng.uniform(0.0, 1.0)


def sketch_iso_trapezoid2(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint], rng: Generator
) -> JGEXPoint:
    a, b, c = args
    d1 = c.foot(JGEXLine(a, b))
    return c + (b - d1) + (a - d1)


def sketch_acute_triangle(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    a, b = random_points(2, rng)
    # The locus of points such that c makes triangle a b c acute (with these specific a, b)
    # is such that (more or less) the x coordinate of c is between 0,1
    # and the y coordinate has to be above the circle with center .5,0
    # and radius .5 (if it is on the circle it is right, if it is below the circle then it is obtuse).
    t = rng.uniform(0, 1)
    length = a.distance(b)
    v = b - a
    height_min = np.sqrt(length**2 - ((t - 0.5) * length) ** 2)
    height = float(rng.uniform(height_min, 2.5 * height_min))  # pyright: ignore
    c = a + t * v + height * v.rot90()
    a, b, c = random_rfss(a, b, c, rng=rng)
    return a, b, c


def sketch_cc_itangent(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint, JGEXPoint], **kwargs: Any
) -> tuple[JGEXPoint, ...]:
    """Sketch internal tangents to two circles."""
    o, a, w, b = args
    ra, rb = o.distance(a), w.distance(b)
    distance = o.distance(w)

    if close_enough(distance, abs(rb + ra)):
        LOGGER.info(
            "The circles are externally tangent. Try another definition of a tangent line."
        )
    elif distance < abs(rb + ra):
        LOGGER.info(
            "The circles intersect or one is inside the other. There are no internal tangents"
        )

    oa = JGEXCircle(o, ra)
    q = o + (w - o) * ra / (ra + rb)

    x, z = circle_circle_intersection(sketch_dia((o, q)), oa, expected_points=2)
    y = w.foot(JGEXLine(x, q))
    i = w.foot(JGEXLine(z, q))

    return x, y, z, i


def sketch_simtri(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXPoint:
    """Sketch the construction of the third vertex of a similar triangle."""
    A, B, C, P, Q = args
    ab = B - A
    ac = C - A
    pq = Q - P

    ang_ab = np.arctan2(ab.y, ab.x)
    ang_ac = np.arctan2(ac.y, ac.x)
    ang_pq = np.arctan2(pq.y, pq.x)
    ratio = A.distance(B) / P.distance(Q)
    length = A.distance(C) / ratio

    ang_pr = ang_pq + ang_ac - ang_ab
    r = P + length * JGEXPoint(x=np.cos(ang_pr), y=np.sin(ang_pr))
    return r


def sketch_simtrir(args: tuple[JGEXPoint, ...], **kwargs: Any) -> JGEXPoint:
    """Sketch the construction of the third vertex of a similar triangle with a reflection."""
    A, B, C, P, Q = args
    ab = B - A
    ac = C - A
    pq = Q - P

    ang_ab = np.arctan2(ab.y, ab.x)
    ang_ac = np.arctan2(ac.y, ac.x)
    ang_pq = np.arctan2(pq.y, pq.x)
    ratio = A.distance(B) / P.distance(Q)
    length = A.distance(C) / ratio

    ang_pr = ang_pq + ang_ac - ang_ab
    r1 = P + length * JGEXPoint(x=np.cos(ang_pr), y=np.sin(ang_pr))

    r, r2 = circle_circle_intersection(
        JGEXCircle(center=P, p1=r1), JGEXCircle(center=Q, p1=r1), expected_points=2
    )

    if nearly_zero(r.distance(r1)):
        r = r2

    return r


def sketch_contri(
    args: tuple[JGEXPoint, ...], rng: Generator, **kwargs: Any
) -> tuple[JGEXPoint, ...]:
    """Sketch the construction of the vertices of a congruent triangle."""
    A, B, C, P = args

    # rotation parameters
    ang = rng.uniform(0.0, 2 * np.pi)
    sin, cos = np.sin(ang), np.cos(ang)

    # take triangle to the origin
    q1 = B - A
    r1 = C - A

    # rotate the triangle
    q2 = q1.rotate(sin, cos)
    r2 = r1.rotate(sin, cos)

    # position triangle based on P
    q = q2 + P
    r = r2 + P

    return q, r


def sketch_contrir(
    args: tuple[JGEXPoint, ...], rng: Generator, **kwargs: Any
) -> tuple[JGEXPoint, ...]:
    """Sketch the construction of the vertices of a congruent triangle with a reflection."""
    A, B, C, P = args

    # rotation parameters
    ang = rng.uniform(0.0, 2 * np.pi)
    sin, cos = np.sin(ang), np.cos(ang)

    # take triangle to the origin
    q1 = B - A
    r1 = C - A

    # rotate the triangle
    q2 = q1.rotate(sin, cos)
    r2 = r1.rotate(sin, cos)

    # position triangle based on P
    q = q2 + P
    r3 = r2 + P

    r, r4 = circle_circle_intersection(
        JGEXCircle(center=P, p1=r3), JGEXCircle(center=q, p1=r3), expected_points=2
    )

    if nearly_zero(r.distance(r3)):
        r = r4

    return q, r


def sketch_test_r20(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    b = JGEXPoint(x=0.0, y=0.0)
    a = JGEXPoint(x=0.0, y=rng.uniform(0.5, 2.0))
    c = JGEXPoint(x=rng.uniform(0.5, 2.0), y=0.0)
    o = (a + c) * 0.5
    o, a, b, c = random_rfss(o, a, b, c, rng=rng)
    return o, a, b, c


def sketch_test_r25(
    args: tuple[JGEXPoint, ...], rng: Generator
) -> tuple[JGEXPoint, ...]:
    a, b, c = random_points(3, rng)
    m = (a + b) * 0.5
    d = b + a - c
    return a, b, c, d, m


def sketch_l2const(args: tuple[JGEXPoint, str], **kwargs: Any) -> JGEXCircle:
    """Sketches point x such that x in at lenght sqrt(l) of point a"""

    a, l2 = args
    squared_length = float(str_to_fraction(l2))
    radius = squared_length**0.5
    return JGEXCircle(center=a, radius=radius)


def sketch_r2const(
    args: tuple[JGEXPoint, JGEXPoint, JGEXPoint, str], **kwargs: Any
) -> JGEXCircle:
    """Sketches point x such that (ab/cx)^2=r"""
    A, B, C, r = args
    dab = A.distance(B)
    length = float(dab / (float(str_to_fraction(r) ** 0.5)))
    return JGEXCircle(center=C, radius=length)
