from __future__ import annotations
from typing import TYPE_CHECKING
from newclid.predicates import Predicate
import newclid.geometry as gm

from newclid._lazy_loading import lazy_import
from newclid.numerical import ATOM, close_enough
from newclid.numerical.angles import ang_between
from newclid.numerical.geometries import CircleNum, LineNum, PointNum, bring_together
from newclid.listing import list_eqratio3
from newclid.statements.statement import Statement, angle_to_num_den, ratio_to_num_den

if TYPE_CHECKING:
    import numpy

np: "numpy" = lazy_import("numpy")


def check_circle_numerical(points: list[PointNum]) -> bool:
    if len(points) != 4:
        return False
    o, a, b, c = points
    oa, ob, oc = o.distance(a), o.distance(b), o.distance(c)
    return close_enough(oa, ob) and close_enough(ob, oc)


def check_coll_numerical(points: list[PointNum]) -> bool:
    a, b = points[:2]
    line = LineNum(a, b)
    for p in points[2:]:
        if abs(line(p.x, p.y)) > ATOM:
            return False
    return True


def check_ncoll_numerical(points: list[PointNum]) -> bool:
    return not check_coll_numerical(points)


def check_sangle_numerical(args: list[PointNum | gm.Angle]) -> bool:
    a, b, c, angle = args
    num, den = angle_to_num_den(angle)
    ang = ang_between(b, c, a)
    # if ang < -ATOM:
    if ang < 0:
        ang += np.pi
    return close_enough(ang, num * np.pi / den)


def check_aconst_numerical(args: list[PointNum | gm.Angle]) -> bool:
    a, b, c, d, angle = args
    num, den = angle_to_num_den(angle)
    d = d + a - c
    ang = ang_between(a, b, d)
    # if ang < -ATOM:
    if ang < 0:
        ang += np.pi
    return close_enough(ang, num * np.pi / den)


def check_sameside_numerical(points: list[PointNum]) -> bool:
    b, a, c, y, x, z = points
    # whether b is to the same side of a & c as y is to x & z
    ba = b - a
    bc = b - c
    yx = y - x
    yz = y - z
    # return ba.dot(bc) * yx.dot(yz) > ATOM
    return ba.dot(bc) * yx.dot(yz) > 0


def check_para_numerical(points: list[PointNum]) -> bool:
    a, b, c, d = points
    ab = LineNum(a, b)
    cd = LineNum(c, d)
    if ab.same(cd):
        return False
    return ab.is_parallel(cd)


def check_para_or_coll_numerical(points: list[PointNum]) -> bool:
    return check_para_numerical(points) or check_coll_numerical(points)


def check_perp_numerical(points: list[PointNum]) -> bool:
    a, b, c, d = points
    ab = LineNum(a, b)
    cd = LineNum(c, d)
    return ab.is_perp(cd)


def check_cyclic_numerical(points: list[PointNum]) -> bool:
    points = list(set(points))
    a, b, c, *ps = points
    circle = CircleNum(p1=a, p2=b, p3=c)
    for d in ps:
        if not close_enough(d.distance(circle.center), circle.radius):
            return False
    return True


def check_const_angle_numerical(points: list[PointNum]) -> bool:
    """Check if the angle is equal to the given constant."""
    a, b, c, d, m, n = points
    a, b, c, d = bring_together(a, b, c, d)
    ba = b - a
    dc = d - c

    a3 = np.arctan2(ba.y, ba.x)
    a4 = np.arctan2(dc.y, dc.x)
    y = a3 - a4

    return close_enough(m / n % 1, y / np.pi % 1)


def check_eqangle_numerical(points: list[PointNum]) -> bool:
    """Check if 8 points make 2 equal angles."""
    a, b, c, d, e, f, g, h = points

    ab = LineNum(a, b)
    cd = LineNum(c, d)
    ef = LineNum(e, f)
    gh = LineNum(g, h)

    if ab.is_parallel(cd):
        return ef.is_parallel(gh)
    if ef.is_parallel(gh):
        return ab.is_parallel(cd)

    a, b, c, d = bring_together(a, b, c, d)
    e, f, g, h = bring_together(e, f, g, h)

    ba = b - a
    dc = d - c
    fe = f - e
    hg = h - g

    sameclock = (ba.x * dc.y - ba.y * dc.x) * (fe.x * hg.y - fe.y * hg.x) > 0
    # sameclock = (ba.x * dc.y - ba.y * dc.x) * (fe.x * hg.y - fe.y * hg.x) > ATOM
    if not sameclock:
        ba = ba * -1.0

    a1 = np.arctan2(fe.y, fe.x)
    a2 = np.arctan2(hg.y, hg.x)
    x = a1 - a2

    a3 = np.arctan2(ba.y, ba.x)
    a4 = np.arctan2(dc.y, dc.x)
    y = a3 - a4

    xy = (x - y) % (2 * np.pi)
    return close_enough(xy, 0) or close_enough(xy, 2 * np.pi)


def check_eqratio_numerical(points: list[PointNum]) -> bool:
    a, b, c, d, e, f, g, h = points
    ab = a.distance(b)
    cd = c.distance(d)
    ef = e.distance(f)
    gh = g.distance(h)
    return close_enough(ab * gh, cd * ef)


def check_eqratio3_numerical(points: list[PointNum]) -> bool:
    for ratio in list_eqratio3(points):
        if not check_eqratio_numerical(ratio):
            return False
    return True


def check_cong_numerical(points: list[PointNum]) -> bool:
    a, b, c, d = points
    return close_enough(a.distance(b), c.distance(d))


def check_midp_numerical(points: list[PointNum]) -> bool:
    a, b, c = points
    return check_coll_numerical(points) and close_enough(a.distance(b), a.distance(c))


def check_simtri_numerical(points: list[PointNum]) -> bool:
    """Check if 6 points make a pair of similar triangles."""
    a, b, c, x, y, z = points
    ab = a.distance(b)
    bc = b.distance(c)
    ca = c.distance(a)
    xy = x.distance(y)
    yz = y.distance(z)
    zx = z.distance(x)
    return close_enough(ab * yz, bc * xy) and close_enough(bc * zx, ca * yz)


def check_contri_numerical(points: list[PointNum]) -> bool:
    a, b, c, x, y, z = points
    ab = a.distance(b)
    bc = b.distance(c)
    ca = c.distance(a)
    xy = x.distance(y)
    yz = y.distance(z)
    zx = z.distance(x)
    return close_enough(ab, xy) and close_enough(bc, yz) and close_enough(ca, zx)


def check_ratio_numerical(points: list[PointNum | gm.Ratio]) -> bool:
    a, b, c, d, ratio = points
    m, n = ratio_to_num_den(ratio)
    ab = a.distance(b)
    cd = c.distance(d)
    return close_enough(ab * n, cd * m)


def check_length_numerical(points: list[PointNum | gm.Length]) -> bool:
    a, b, length = points
    ab = a.distance(b)
    return close_enough(ab, float(length.name))


PREDICATE_TO_NUMERICAL_CHECK = {
    Predicate.COLLINEAR: check_coll_numerical,
    Predicate.PERPENDICULAR: check_perp_numerical,
    Predicate.MIDPOINT: check_midp_numerical,
    Predicate.CONGRUENT: check_cong_numerical,
    Predicate.CIRCLE: check_circle_numerical,
    Predicate.CYCLIC: check_cyclic_numerical,
    Predicate.EQANGLE: check_eqangle_numerical,
    Predicate.EQANGLE6: check_eqangle_numerical,
    Predicate.EQRATIO: check_eqratio_numerical,
    Predicate.EQRATIO3: check_eqratio3_numerical,
    Predicate.EQRATIO6: check_eqratio_numerical,
    Predicate.SIMILAR_TRIANGLE: check_simtri_numerical,
    Predicate.SIMILAR_TRIANGLE_REFLECTED: check_simtri_numerical,
    Predicate.SIMILAR_TRIANGLE_BOTH: check_simtri_numerical,
    Predicate.CONTRI_TRIANGLE: check_contri_numerical,
    Predicate.CONTRI_TRIANGLE_REFLECTED: check_contri_numerical,
    Predicate.CONTRI_TRIANGLE_BOTH: check_contri_numerical,
    Predicate.CONSTANT_ANGLE: check_aconst_numerical,
    Predicate.S_ANGLE: check_sangle_numerical,
    Predicate.SAMESIDE: check_sameside_numerical,
    Predicate.NON_COLLINEAR: check_ncoll_numerical,
    Predicate.CONSTANT_RATIO: check_ratio_numerical,
    Predicate.CONSTANT_LENGTH: check_length_numerical,
    Predicate.PARALLEL: check_para_or_coll_numerical,
}


def check_numerical(statement: Statement) -> bool:
    """Numerical check."""

    if statement.predicate in [
        Predicate.COMPUTE_RATIO,
        Predicate.COMPUTE_ANGLE,
        Predicate.FIX_L,
        Predicate.FIX_C,
        Predicate.FIX_B,
        Predicate.FIX_T,
        Predicate.FIX_P,
    ]:
        return True

    num_args = [p.num if isinstance(p, gm.Point) else p for p in statement.args]
    return PREDICATE_TO_NUMERICAL_CHECK[statement.predicate](num_args)


def same_clock(
    a: PointNum, b: PointNum, c: PointNum, d: PointNum, e: PointNum, f: PointNum
) -> bool:
    return clock(a, b, c) * clock(d, e, f) > 0
    # return clock(a, b, c) * clock(d, e, f) > ATOM


def clock(a: PointNum, b: PointNum, c: PointNum):
    ba = b - a
    cb = c - b
    return ba.x * cb.y - ba.y * cb.x


def same_sign(
    a: PointNum, b: PointNum, c: PointNum, d: PointNum, e: PointNum, f: PointNum
) -> bool:
    a, b, c, d, e, f = map(lambda p: p.sym, [a, b, c, d, e, f])
    ab, cb = a - b, c - b
    de, fe = d - e, f - e
    return (ab.x * cb.y - ab.y * cb.x) * (de.x * fe.y - de.y * fe.x) > 0
    # return (ab.x * cb.y - ab.y * cb.x) * (de.x * fe.y - de.y * fe.x) > ATOM
