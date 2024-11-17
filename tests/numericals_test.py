# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Unit testing for the geometry numericals code."""

import pytest_check as check

import newclid.numericals as nm

np = nm.np

unif = nm.unif
Point = nm.Point
Line = nm.Line
Circle = nm.Circle
HalfLine = nm.HalfLine

line_circle_intersection = nm.line_circle_intersection
line_line_intersection = nm.line_line_intersection

check_coll = nm.check_coll
check_eqangle = nm.check_eqangle

random_points = nm.random_points
ang_between = nm.ang_between
head_from = nm.head_from


class TestNumerical:
    def test_sketch_ieq_triangle(self):
        a, b, c = nm.sketch_ieq_triangle([])
        check.almost_equal(a.distance(b), b.distance(c))
        check.almost_equal(c.distance(a), b.distance(c))

    def test_sketch_2l1c(self):
        p = nm.Point(0.0, 0.0)
        pi = np.pi
        anga = unif(-0.4 * pi, 0.4 * pi)
        a = Point(np.cos(anga), np.sin(anga))
        angb = unif(0.6 * pi, 1.4 * pi)
        b = Point(np.cos(angb), np.sin(angb))

        angc = unif(anga + 0.05 * pi, angb - 0.05 * pi)
        c = Point(np.cos(angc), np.sin(angc)) * unif(0.2, 0.8)

        x, y, z, i = nm.sketch_2l1c([a, b, c, p])
        check.is_true(check_coll([x, c, a]))
        check.is_true(check_coll([y, c, b]))
        check.almost_equal(z.distance(p), 1.0)
        check.is_true(check_coll([p, i, z]))
        check.is_true(Line(i, x).is_perp(Line(c, a)))
        check.is_true(Line(i, y).is_perp(Line(c, b)))
        check.almost_equal(i.distance(x), i.distance(y))
        check.almost_equal(i.distance(x), i.distance(z))

    def test_sketch_3peq(self):
        a, b, c = random_points(3)
        x, y, z = nm.sketch_3peq([a, b, c])

        check.is_true(check_coll([a, b, x]))
        check.is_true(check_coll([a, c, y]))
        check.is_true(check_coll([b, c, z]))
        check.is_true(check_coll([x, y, z]))
        check.almost_equal(z.distance(x), z.distance(y))

    def test_sketch_aline(self):
        a, b, c, d, e = random_points(5)
        ex = nm.sketch_aline([a, b, c, d, e])
        check.is_instance(ex, HalfLine)
        check.equal(ex.tail, e)
        x = ex.head
        check.almost_equal(ang_between(b, a, c), ang_between(e, d, x))

    def test_sketch_amirror(self):
        a, b, c = random_points(3)
        bx = nm.sketch_amirror([a, b, c])
        check.is_instance(bx, HalfLine)
        assert bx.tail == b
        x = bx.head

        ang1 = ang_between(b, a, c)
        ang2 = ang_between(b, c, x)
        check.almost_equal(ang1, ang2)

    def test_sketch_bisect(self):
        a, b, c = random_points(3)
        line = nm.sketch_bisect([a, b, c])
        check.almost_equal(b.distance(line), 0.0)

        perpendicular_line = a.perpendicular_line(line)
        x = line_line_intersection(perpendicular_line, Line(b, c))
        check.almost_equal(a.distance(line), x.distance(line))

        d, _ = line_circle_intersection(line, Circle(b, radius=1))
        ang1 = ang_between(b, a, d)
        ang2 = ang_between(b, d, c)
        check.almost_equal(ang1, ang2)

    def test_sketch_bline(self):
        a, b = random_points(2)
        line_ab = nm.sketch_bline([a, b])
        check.is_true(Line(a, b).is_perp(line_ab))
        check.almost_equal(a.distance(line_ab), b.distance(line_ab))

    def test_sketch_cc_tangent(self):
        o = Point(0.0, 0.0)
        w = Point(1.0, 0.0)

        ra = unif(0.0, 0.6)
        rb = unif(0.4, 1.0)

        a = unif(0.0, np.pi)
        b = unif(0.0, np.pi)

        a = o + ra * Point(np.cos(a), np.sin(a))
        b = w + rb * Point(np.sin(b), np.cos(b))

        x, y, z, t = nm.sketch_cc_tangent([o, a, w, b])
        xy = Line(x, y)
        zt = Line(z, t)
        check.almost_equal(o.distance(xy), o.distance(a))
        check.almost_equal(o.distance(zt), o.distance(a))
        check.almost_equal(w.distance(xy), w.distance(b))
        check.almost_equal(w.distance(zt), w.distance(b))

    def test_sketch_circle(self):
        a, b, c = random_points(3)
        circle = nm.sketch_circle([a, b, c])
        check.almost_equal(circle.center.distance(a), 0.0)
        check.almost_equal(circle.radius, b.distance(c))

    def test_sketch_e5128(self):
        b = Point(0.0, 0.0)
        c = Point(0.0, 1.0)
        ang = unif(-np.pi / 2, 3 * np.pi / 2)
        d = head_from(c, ang, 1.0)
        a = Point(unif(0.5, 2.0), 0.0)

        e, g = nm.sketch_e5128([a, b, c, d])
        ang1 = ang_between(a, b, d)
        ang2 = ang_between(e, a, g)
        check.almost_equal(ang1, ang2)

    def test_sketch_eq_quadrangle(self):
        a, b, c, d = nm.sketch_eq_quadrangle([])
        check.almost_equal(a.distance(d), c.distance(b))
        ac = Line(a, c)
        assert ac.diff_side(b, d), (ac(b), ac(d))
        bd = Line(b, d)
        assert bd.diff_side(a, c), (bd(a), bd(c))

    def test_sketch_eq_trapezoid(self):
        a, b, c, d = nm.sketch_eq_trapezoid([])
        assert Line(a, b).is_parallel(Line(c, d))
        check.almost_equal(a.distance(d), b.distance(c))

    def test_sketch_eqangle3(self):
        points = random_points(5)
        x = nm.sketch_eqangle3(points).sample_within(points)[0]
        a, b, d, e, f = points
        check.is_true(check_eqangle([x, a, x, b, d, e, d, f]))

    def test_sketch_eqangle2(self):
        a, b, c = random_points(3)
        x = nm.sketch_eqangle2([a, b, c])
        ang1 = ang_between(a, b, x)
        ang2 = ang_between(c, x, b)
        check.almost_equal(ang1, ang2)

    def test_sketch_edia_quadrangle(self):
        a, b, c, d = nm.sketch_eqdia_quadrangle([])
        assert Line(a, c).diff_side(b, d)
        assert Line(b, d).diff_side(a, c)
        check.almost_equal(a.distance(c), b.distance(d))

    def test_sketch_isos(self):
        a, b, c = nm.sketch_isos([])
        check.almost_equal(a.distance(b), a.distance(c))
        check.almost_equal(ang_between(b, a, c), ang_between(c, b, a))

    def test_sketch_quadrange(self):
        a, b, c, d = nm.sketch_quadrangle([])
        check.is_true(Line(a, c).diff_side(b, d))
        check.is_true(Line(b, d).diff_side(a, c))

    def test_sketch_r_trapezoid(self):
        a, b, c, d = nm.sketch_r_trapezoid([])
        check.is_true(Line(a, b).is_perp(Line(a, d)))
        check.is_true(Line(a, b).is_parallel(Line(c, d)))
        check.is_true(Line(a, c).diff_side(b, d))
        check.is_true(Line(b, d).diff_side(a, c))

    def test_sketch_r_triangle(self):
        a, b, c = nm.sketch_r_triangle([])
        check.is_true(Line(a, b).is_perp(Line(a, c)))

    def test_sketch_rectangle(self):
        a, b, c, d = nm.sketch_rectangle([])
        check.is_true(Line(a, b).is_perp(Line(b, c)))
        check.is_true(Line(b, c).is_perp(Line(c, d)))
        check.is_true(Line(c, d).is_perp(Line(d, a)))

    def test_sketch_reflect(self):
        a, b, c = random_points(3)
        x = nm.sketch_reflect([a, b, c])
        check.is_true(Line(a, x).is_perp(Line(b, c)))
        check.almost_equal(x.distance(Line(b, c)), a.distance(Line(b, c)))

    def test_sketch_risos(self):
        a, b, c = nm.sketch_risos([])
        check.almost_equal(a.distance(b), a.distance(c))
        check.is_true(Line(a, b).is_perp(Line(a, c)))

    def test_sketch_rotaten90(self):
        a, b = random_points(2)
        x = nm.sketch_rotaten90([a, b])
        check.almost_equal(a.distance(x), a.distance(b))
        check.is_true(Line(a, x).is_perp(Line(a, b)))
        d = Point(0.0, 0.0)
        e = Point(0.0, 1.0)
        f = Point(1.0, 0.0)
        check.almost_equal(ang_between(d, e, f), ang_between(a, b, x))

    def test_sketch_rotatep90(self):
        a, b = random_points(2)
        x = nm.sketch_rotatep90([a, b])
        check.almost_equal(a.distance(x), a.distance(b))
        check.is_true(Line(a, x).is_perp(Line(a, b)))
        d = Point(0.0, 0.0)
        e = Point(0.0, 1.0)
        f = Point(1.0, 0.0)
        check.almost_equal(ang_between(d, f, e), ang_between(a, b, x))

    def test_sketch_s_angle(self):
        a, b = random_points(2)
        y = unif(0.0, np.pi)
        bx = nm.sketch_s_angle([a, b, y / np.pi * 180])
        check.is_instance(bx, HalfLine)
        check.equal(bx.tail, b)
        x = bx.head

        d = Point(1.0, 0.0)
        e = Point(0.0, 0.0)
        f = Point(np.cos(y), np.sin(y))
        check.almost_equal(ang_between(e, d, f), ang_between(b, a, x))

    def test_sketch_shift(self):
        a, b, c = random_points(3)
        x = nm.sketch_shift([a, b, c])
        check.is_true((b - a).close(x - c))

    def test_sketch_square(self):
        a, b = random_points(2)
        c, d = nm.sketch_square([a, b])
        check.is_true(Line(a, b).is_perp(Line(b, c)))
        check.is_true(Line(b, c).is_perp(Line(c, d)))
        check.is_true(Line(c, d).is_perp(Line(d, a)))
        check.almost_equal(a.distance(b), b.distance(c))

    def test_sketch_isquare(self):
        a, b, c, d = nm.sketch_isquare([])
        check.is_true(Line(a, b).is_perp(Line(b, c)))
        check.is_true(Line(b, c).is_perp(Line(c, d)))
        check.is_true(Line(c, d).is_perp(Line(d, a)))
        check.almost_equal(a.distance(b), b.distance(c))

    def test_sketch_trapezoid(self):
        a, b, c, d = nm.sketch_trapezoid([])
        check.is_true(Line(a, b).is_parallel(Line(c, d)))
        check.is_true(Line(a, c).diff_side(b, d))
        check.is_true(Line(b, d).diff_side(a, c))

    def test_sketch_triangle(self):
        a, b, c = nm.sketch_triangle([])
        check.is_false(check_coll([a, b, c]))

    def test_sketch_triangle12(self):
        a, b, c = nm.sketch_triangle12([])
        check.almost_equal(a.distance(b) * 2, a.distance(c))

    def test_sketch_trisect(self):
        a, b, c = random_points(3)
        x, y = nm.sketch_trisect([a, b, c])
        check.almost_equal(ang_between(b, a, x), ang_between(b, x, y))
        check.almost_equal(ang_between(b, x, y), ang_between(b, y, c))
        check.almost_equal(ang_between(b, a, x) * 3, ang_between(b, a, c))

    def test_sketch_trisegment(self):
        a, b = random_points(2)
        x, y = nm.sketch_trisegment([a, b])
        check.almost_equal(a.distance(x) + x.distance(y) + y.distance(b), a.distance(b))
        check.almost_equal(a.distance(x), x.distance(y))
        check.almost_equal(x.distance(y), y.distance(b))
