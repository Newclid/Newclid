"""Unit testing for the geometry numericals code."""

import numpy as np
import pytest_check as check
from newclid.geometry import Angle
from newclid.numerical.angles import ang_between
from newclid.numerical.check import check_coll_numerical, check_eqangle_numerical
from newclid.numerical.geometries import (
    CircleNum,
    HalfLine,
    LineNum,
    PointNum,
    line_circle_intersection,
    line_line_intersection,
)
from newclid.numerical.sketch import (
    head_from,
    sketch_2l1c,
    sketch_3peq,
    sketch_aline,
    sketch_amirror,
    sketch_bisect,
    sketch_bline,
    sketch_cc_tangent,
    sketch_circle,
    sketch_e5128,
    sketch_eq_quadrangle,
    sketch_iso_trapezoid,
    sketch_eqangle2,
    sketch_eqangle3,
    sketch_eqdia_quadrangle,
    sketch_ieq_triangle,
    sketch_isos,
    sketch_isquare,
    sketch_quadrangle,
    sketch_r_trapezoid,
    sketch_r_triangle,
    sketch_rectangle,
    sketch_reflect,
    sketch_risos,
    sketch_rotaten90,
    sketch_rotatep90,
    sketch_s_angle,
    sketch_shift,
    sketch_square,
    sketch_trapezoid,
    sketch_triangle,
    sketch_triangle12,
    sketch_trisect,
    sketch_trisegment,
)
import newclid.numerical.sketch
from newclid.ratios import simplify


class TestNumerical:
    def test_sketch_ieq_triangle(self):
        rnd_gen = np.random.default_rng()
        a, b, c = sketch_ieq_triangle([], rnd_gen=rnd_gen)
        check.almost_equal(a.distance(b), b.distance(c))
        check.almost_equal(c.distance(a), b.distance(c))

    def test_sketch_2l1c(self):
        rnd_gen = np.random.default_rng()
        p = PointNum(0.0, 0.0)
        pi = np.pi
        anga = rnd_gen.uniform(-0.4 * pi, 0.4 * pi)
        a = PointNum(np.cos(anga), np.sin(anga))
        angb = rnd_gen.uniform(0.6 * pi, 1.4 * pi)
        b = PointNum(np.cos(angb), np.sin(angb))

        angc = rnd_gen.uniform(anga + 0.05 * pi, angb - 0.05 * pi)
        c = PointNum(np.cos(angc), np.sin(angc)) * rnd_gen.uniform(0.2, 0.8)

        x, y, z, i = sketch_2l1c([a, b, c, p])
        check.is_true(check_coll_numerical([x, c, a]))
        check.is_true(check_coll_numerical([y, c, b]))
        check.almost_equal(z.distance(p), 1.0)
        check.is_true(check_coll_numerical([p, i, z]))
        check.is_true(LineNum(i, x).is_perp(LineNum(c, a)))
        check.is_true(LineNum(i, y).is_perp(LineNum(c, b)))
        check.almost_equal(i.distance(x), i.distance(y))
        check.almost_equal(i.distance(x), i.distance(z))

    def test_sketch_3peq(self):
        rnd_gen = np.random.default_rng()
        a, b, c = newclid.numerical.sketch.random_points(3, rnd_gen)
        x, y, z = sketch_3peq([a, b, c], rnd_gen=rnd_gen)

        check.is_true(check_coll_numerical([a, b, x]))
        check.is_true(check_coll_numerical([a, c, y]))
        check.is_true(check_coll_numerical([b, c, z]))
        check.is_true(check_coll_numerical([x, y, z]))
        check.almost_equal(z.distance(x), z.distance(y))

    def test_sketch_aline(self):
        rnd_gen = np.random.default_rng()
        a, b, c, d, e = newclid.numerical.sketch.random_points(5, rnd_gen)
        ex = sketch_aline([a, b, c, d, e])
        check.is_instance(ex, HalfLine)
        check.equal(ex.tail, e)
        x = ex.head
        check.almost_equal(ang_between(b, a, c), ang_between(e, d, x))

    def test_sketch_amirror(self):
        rnd_gen = np.random.default_rng()
        a, b, c = newclid.numerical.sketch.random_points(3, rnd_gen)
        bx = sketch_amirror([a, b, c])
        check.is_instance(bx, HalfLine)
        assert bx.tail == b
        x = bx.head

        ang1 = ang_between(b, a, c)
        ang2 = ang_between(b, c, x)
        check.almost_equal(ang1, ang2)

    def test_sketch_bisect(self):
        rnd_gen = np.random.default_rng()
        a, b, c = newclid.numerical.sketch.random_points(3, rnd_gen)
        line = sketch_bisect([a, b, c])
        check.almost_equal(b.distance(line), 0.0)

        perpendicular_line = a.perpendicular_line(line)
        x = line_line_intersection(perpendicular_line, LineNum(b, c))
        check.almost_equal(a.distance(line), x.distance(line))

        d, _ = line_circle_intersection(line, CircleNum(b, radius=1))
        ang1 = ang_between(b, a, d)
        ang2 = ang_between(b, d, c)
        check.almost_equal(ang1, ang2)

    def test_sketch_bline(self):
        rnd_gen = np.random.default_rng()
        a, b = newclid.numerical.sketch.random_points(2, rnd_gen)
        line_ab = sketch_bline([a, b])
        check.is_true(LineNum(a, b).is_perp(line_ab))
        check.almost_equal(a.distance(line_ab), b.distance(line_ab))

    def test_sketch_cc_tangent(self):
        rnd_gen = np.random.default_rng()

        o = PointNum(0.0, 0.0)
        w = PointNum(1.0, 0.0)

        ra = rnd_gen.uniform(0.0, 0.6)
        rb = rnd_gen.uniform(0.4, 1.0)

        a = rnd_gen.uniform(0.0, np.pi)
        b = rnd_gen.uniform(0.0, np.pi)

        a = o + ra * PointNum(np.cos(a), np.sin(a))
        b = w + rb * PointNum(np.sin(b), np.cos(b))

        x, y, z, t = sketch_cc_tangent([o, a, w, b])
        xy = LineNum(x, y)
        zt = LineNum(z, t)
        check.almost_equal(o.distance(xy), o.distance(a))
        check.almost_equal(o.distance(zt), o.distance(a))
        check.almost_equal(w.distance(xy), w.distance(b))
        check.almost_equal(w.distance(zt), w.distance(b))

    def test_sketch_circle(self):
        rnd_gen = np.random.default_rng()
        a, b, c = newclid.numerical.sketch.random_points(3, rnd_gen)
        circle = sketch_circle([a, b, c])
        check.almost_equal(circle.center.distance(a), 0.0)
        check.almost_equal(circle.radius, b.distance(c))

    def test_sketch_e5128(self):
        rnd_gen = np.random.default_rng()
        b = PointNum(0.0, 0.0)
        c = PointNum(0.0, 1.0)
        ang = rnd_gen.uniform(-np.pi / 2, 3 * np.pi / 2)
        d = head_from(c, ang, 1.0)
        a = PointNum(rnd_gen.uniform(0.5, 2.0), 0.0)

        e, g = sketch_e5128([a, b, c, d])
        ang1 = ang_between(a, b, d)
        ang2 = ang_between(e, a, g)
        check.almost_equal(ang1, ang2)

    def test_sketch_eq_quadrangle(self):
        rnd_gen = np.random.default_rng()
        a, b, c, d = sketch_eq_quadrangle([], rnd_gen=rnd_gen)
        check.almost_equal(a.distance(d), c.distance(b))
        ac = LineNum(a, c)
        assert ac.diff_side(b, d), (ac(b), ac(d))
        bd = LineNum(b, d)
        assert bd.diff_side(a, c), (bd(a), bd(c))

    def test_sketch_iso_trapezoid(self):
        rnd_gen = np.random.default_rng()
        a, b, c, d = sketch_iso_trapezoid([], rnd_gen=rnd_gen)
        assert LineNum(a, b).is_parallel(LineNum(c, d))
        check.almost_equal(a.distance(d), b.distance(c))

    def test_sketch_eqangle3(self):
        rnd_gen = np.random.default_rng()
        points = newclid.numerical.sketch.random_points(5, rnd_gen=rnd_gen)
        x = sketch_eqangle3(points).sample_within(points, rnd_gen=rnd_gen)[0]
        a, b, d, e, f = points
        check.is_true(check_eqangle_numerical([x, a, x, b, d, e, d, f]))

    def test_sketch_eqangle2(self):
        rnd_gen = np.random.default_rng()
        a, b, c = newclid.numerical.sketch.random_points(3, rnd_gen)
        x = sketch_eqangle2([a, b, c], rnd_gen=rnd_gen)
        ang1 = ang_between(a, b, x)
        ang2 = ang_between(c, x, b)
        check.almost_equal(ang1, ang2)

    def test_sketch_edia_quadrangle(self):
        rnd_gen = np.random.default_rng()
        a, b, c, d = sketch_eqdia_quadrangle([], rnd_gen=rnd_gen)
        assert LineNum(a, c).diff_side(b, d)
        assert LineNum(b, d).diff_side(a, c)
        check.almost_equal(a.distance(c), b.distance(d))

    def test_sketch_isos(self):
        rnd_gen = np.random.default_rng()
        a, b, c = sketch_isos([], rnd_gen=rnd_gen)
        check.almost_equal(a.distance(b), a.distance(c))
        check.almost_equal(ang_between(b, a, c), ang_between(c, b, a))

    def test_sketch_quadrange(self):
        rnd_gen = np.random.default_rng()
        a, b, c, d = sketch_quadrangle([], rnd_gen=rnd_gen)
        check.is_true(LineNum(a, c).diff_side(b, d))
        check.is_true(LineNum(b, d).diff_side(a, c))

    def test_sketch_r_trapezoid(self):
        rnd_gen = np.random.default_rng()
        a, b, c, d = sketch_r_trapezoid([], rnd_gen=rnd_gen)
        check.is_true(LineNum(a, b).is_perp(LineNum(a, d)))
        check.is_true(LineNum(a, b).is_parallel(LineNum(c, d)))
        check.is_true(LineNum(a, c).diff_side(b, d))
        check.is_true(LineNum(b, d).diff_side(a, c))

    def test_sketch_r_triangle(self):
        rnd_gen = np.random.default_rng()
        a, b, c = sketch_r_triangle([], rnd_gen=rnd_gen)
        check.is_true(LineNum(a, b).is_perp(LineNum(a, c)))

    def test_sketch_rectangle(self):
        rnd_gen = np.random.default_rng()
        a, b, c, d = sketch_rectangle([], rnd_gen=rnd_gen)
        check.is_true(LineNum(a, b).is_perp(LineNum(b, c)))
        check.is_true(LineNum(b, c).is_perp(LineNum(c, d)))
        check.is_true(LineNum(c, d).is_perp(LineNum(d, a)))

    def test_sketch_reflect(self):
        rnd_gen = np.random.default_rng()
        a, b, c = newclid.numerical.sketch.random_points(3, rnd_gen)
        x = sketch_reflect([a, b, c])
        check.is_true(LineNum(a, x).is_perp(LineNum(b, c)))
        check.almost_equal(x.distance(LineNum(b, c)), a.distance(LineNum(b, c)))

    def test_sketch_risos(self):
        rnd_gen = np.random.default_rng()
        a, b, c = sketch_risos([], rnd_gen=rnd_gen)
        check.almost_equal(a.distance(b), a.distance(c))
        check.is_true(LineNum(a, b).is_perp(LineNum(a, c)))

    def test_sketch_rotaten90(self):
        rnd_gen = np.random.default_rng()
        a, b = newclid.numerical.sketch.random_points(2, rnd_gen)
        x = sketch_rotaten90([a, b])
        check.almost_equal(a.distance(x), a.distance(b))
        check.is_true(LineNum(a, x).is_perp(LineNum(a, b)))
        d = PointNum(0.0, 0.0)
        e = PointNum(0.0, 1.0)
        f = PointNum(1.0, 0.0)
        check.almost_equal(ang_between(d, e, f), ang_between(a, b, x))

    def test_sketch_rotatep90(self):
        rnd_gen = np.random.default_rng()
        a, b = newclid.numerical.sketch.random_points(2, rnd_gen)
        x = sketch_rotatep90([a, b])
        check.almost_equal(a.distance(x), a.distance(b))
        check.is_true(LineNum(a, x).is_perp(LineNum(a, b)))
        d = PointNum(0.0, 0.0)
        e = PointNum(0.0, 1.0)
        f = PointNum(1.0, 0.0)
        check.almost_equal(ang_between(d, f, e), ang_between(a, b, x))

    def test_sketch_s_angle(self):
        rnd_gen = np.random.default_rng()
        a, b = newclid.numerical.sketch.random_points(2, rnd_gen)
        num = rnd_gen.uniform(0.0, 180.0)
        num, den = simplify(int(num), 180)
        ang = num * np.pi / den
        y = Angle(f"{num}pi/{den}")
        bx = sketch_s_angle([a, b, y])
        check.is_instance(bx, HalfLine)
        check.equal(bx.tail, b)
        x = bx.head

        d = PointNum(1.0, 0.0)
        e = PointNum(0.0, 0.0)
        f = PointNum(np.cos(ang), np.sin(ang))
        check.almost_equal(ang_between(e, d, f), ang_between(b, a, x))

    def test_sketch_shift(self):
        rnd_gen = np.random.default_rng()
        a, b, c = newclid.numerical.sketch.random_points(3, rnd_gen)
        x = sketch_shift([a, b, c])
        check.is_true((b - a).close(x - c))

    def test_sketch_square(self):
        rnd_gen = np.random.default_rng()
        a, b = newclid.numerical.sketch.random_points(2, rnd_gen)
        c, d = sketch_square([a, b])
        check.is_true(LineNum(a, b).is_perp(LineNum(b, c)))
        check.is_true(LineNum(b, c).is_perp(LineNum(c, d)))
        check.is_true(LineNum(c, d).is_perp(LineNum(d, a)))
        check.almost_equal(a.distance(b), b.distance(c))

    def test_sketch_isquare(self):
        a, b, c, d = sketch_isquare([], rnd_gen=np.random.default_rng())
        check.is_true(LineNum(a, b).is_perp(LineNum(b, c)))
        check.is_true(LineNum(b, c).is_perp(LineNum(c, d)))
        check.is_true(LineNum(c, d).is_perp(LineNum(d, a)))
        check.almost_equal(a.distance(b), b.distance(c))

    def test_sketch_trapezoid(self):
        a, b, c, d = sketch_trapezoid([], rnd_gen=np.random.default_rng())
        check.is_true(LineNum(a, b).is_parallel(LineNum(c, d)))
        check.is_true(LineNum(a, c).diff_side(b, d))
        check.is_true(LineNum(b, d).diff_side(a, c))

    def test_sketch_triangle(self):
        a, b, c = sketch_triangle([], rnd_gen=np.random.default_rng())
        check.is_false(check_coll_numerical([a, b, c]))

    def test_sketch_triangle12(self):
        a, b, c = sketch_triangle12([], rnd_gen=np.random.default_rng())
        check.almost_equal(a.distance(b) * 2, a.distance(c))

    def test_sketch_trisect(self):
        rnd_gen = np.random.default_rng()
        a, b, c = newclid.numerical.sketch.random_points(3, rnd_gen)
        x, y = sketch_trisect([a, b, c])
        check.almost_equal(ang_between(b, a, x), ang_between(b, x, y))
        check.almost_equal(ang_between(b, x, y), ang_between(b, y, c))
        check.almost_equal(ang_between(b, a, x) * 3, ang_between(b, a, c))

    def test_sketch_trisegment(self):
        rnd_gen = np.random.default_rng()
        a, b = newclid.numerical.sketch.random_points(2, rnd_gen)
        x, y = sketch_trisegment([a, b])
        check.almost_equal(a.distance(x) + x.distance(y) + y.distance(b), a.distance(b))
        check.almost_equal(a.distance(x), x.distance(y))
        check.almost_equal(x.distance(y), y.distance(b))
