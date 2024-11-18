from typing import TYPE_CHECKING

from newclid.statements.statement import Statement, angle_to_num_den, ratio_to_num_den
from newclid.predicates import Predicate
from newclid.geometry import (
    Angle,
    Circle,
    Length,
    Line,
    Point,
    Ratio,
    all_angles,
    all_lengths,
    all_ratios,
    is_equal,
)
from newclid.numerical.check import (
    check_coll_numerical,
    check_para_numerical,
    check_perp_numerical,
    check_sameside_numerical,
)

from newclid.listing import list_eqratio3


if TYPE_CHECKING:
    from newclid.symbols_graph import SymbolsGraph

from collections import defaultdict


class StatementChecker:
    def __init__(
        self,
        symbols_graph: "SymbolsGraph",
    ) -> None:
        self.symbols_graph = symbols_graph
        self.PREDICATE_TO_CHECK = {
            Predicate.COLLINEAR: self.check_coll,
            Predicate.PARALLEL: self.check_para,
            Predicate.PERPENDICULAR: self.check_perp,
            Predicate.MIDPOINT: self.check_midp,
            Predicate.CONGRUENT: self.check_cong,
            Predicate.CIRCLE: self.check_circle,
            Predicate.CYCLIC: self.check_cyclic,
            Predicate.EQANGLE: self.check_const_or_eqangle,
            Predicate.EQANGLE6: self.check_const_or_eqangle,
            Predicate.EQRATIO: self.check_const_or_eqratio,
            Predicate.EQRATIO3: self.check_eqratio3,
            Predicate.EQRATIO6: self.check_const_or_eqratio,
            Predicate.SIMILAR_TRIANGLE: self.check_simtri,
            Predicate.SIMILAR_TRIANGLE_REFLECTED: self.check_simtri_reflected,
            Predicate.SIMILAR_TRIANGLE_BOTH: self.check_simtri_both,
            Predicate.CONTRI_TRIANGLE: self.check_contri,
            Predicate.CONTRI_TRIANGLE_REFLECTED: self.check_contri_reflected,
            Predicate.CONTRI_TRIANGLE_BOTH: self.check_contri_both,
            Predicate.CONSTANT_ANGLE: self.check_aconst,
            Predicate.S_ANGLE: self.check_sangle,
            Predicate.CONSTANT_RATIO: self.check_rconst,
            Predicate.CONSTANT_LENGTH: self.check_lconst,
            Predicate.COMPUTE_ANGLE: self.check_acompute,
            Predicate.COMPUTE_RATIO: self.check_rcompute,
            Predicate.SAMESIDE: self.check_sameside,
            Predicate.DIFFERENT: self.check_diff,
            Predicate.NON_COLLINEAR: self.check_ncoll,
            Predicate.NON_PARALLEL: self.check_npara,
            Predicate.NON_PERPENDICULAR: self.check_nperp,
        }

    def check(self, statement: Statement) -> bool:
        """Symbolically check if a predicate is True."""
        return self.PREDICATE_TO_CHECK[statement.predicate](statement.args)

    def check_const_or_eqangle(self, args: list[Point]) -> bool:
        if len(args) == 5:
            return self.check_aconst(args)
        return self.check_eqangle(args)

    def check_const_or_eqratio(self, args: list[Point]) -> bool:
        if len(args) == 5:
            return self.check_rconst(args)
        return self.check_eqratio(args)

    # Basic checks

    def check_coll(self, points: list[Point]) -> bool:
        points = list(set(points))
        if len(points) < 3:
            return True
        line2count = defaultdict(lambda: 0)
        for p in points:
            for line in p.neighbors(Line):
                line2count[line] += 1
        return any([count == len(points) for _, count in line2count.items()])

    def check_para(self, points: list[Point]) -> bool:
        a, b, c, d = points
        if (a == b) or (c == d):
            return False
        ab = self.symbols_graph.get_line(a, b)
        cd = self.symbols_graph.get_line(c, d)
        if not ab or not cd:
            return False

        return is_equal(ab, cd)

    def check_para_or_coll(self, points: list[Point]) -> bool:
        return self.check_para(points) or self.check_coll(points)

    def check_perpl(self, ab: Line, cd: Line) -> bool:
        if ab.val is None or cd.val is None:
            return False
        if ab.val == cd.val:
            return False
        a12, a21 = self.symbols_graph.get_angle(ab.val, cd.val)
        if a12 is None or a21 is None:
            return False
        return is_equal(a12, a21)

    def check_perp(self, points: list[Point]) -> bool:
        a, b, c, d = points
        ab = self.symbols_graph.get_line(a, b)
        cd = self.symbols_graph.get_line(c, d)
        if not ab or not cd:
            return False
        return self.check_perpl(ab, cd)

    def check_cong(self, points: list[Point]) -> bool:
        a, b, c, d = points
        if {a, b} == {c, d}:
            return True

        ab = self.symbols_graph.get_segment(a, b)
        cd = self.symbols_graph.get_segment(c, d)
        if ab is None or cd is None:
            return False
        return is_equal(ab, cd)

    # Angles and ratios checks

    def check_eqangle(self, points: list[Point]) -> bool:
        """Check if two angles are equal."""
        a, b, c, d, m, n, p, q = points

        if {a, b} == {c, d} and {m, n} == {p, q}:
            return True
        if {a, b} == {m, n} and {c, d} == {p, q}:
            return True

        if (a == b) or (c == d) or (m == n) or (p == q):
            return False
        ab = self.symbols_graph.get_line(a, b)
        cd = self.symbols_graph.get_line(c, d)
        mn = self.symbols_graph.get_line(m, n)
        pq = self.symbols_graph.get_line(p, q)

        if {a, b} == {c, d} and mn and pq and is_equal(mn, pq):
            return True
        if {a, b} == {m, n} and cd and pq and is_equal(cd, pq):
            return True
        if {p, q} == {m, n} and ab and cd and is_equal(ab, cd):
            return True
        if {p, q} == {c, d} and ab and mn and is_equal(ab, mn):
            return True

        if not ab or not cd or not mn or not pq:
            return False

        if is_equal(ab, cd) and is_equal(mn, pq):
            return True
        if is_equal(ab, mn) and is_equal(cd, pq):
            return True

        if not (ab.val and cd.val and mn.val and pq.val):
            return False

        if (ab.val, cd.val) == (mn.val, pq.val) or (ab.val, mn.val) == (
            cd.val,
            pq.val,
        ):
            return True

        for ang1, _, _ in all_angles(ab._val, cd._val):
            for ang2, _, _ in all_angles(mn._val, pq._val):
                if is_equal(ang1, ang2):
                    return True

        if self.check_perp([a, b, m, n]) and self.check_perp([c, d, p, q]):
            return True
        if self.check_perp([a, b, p, q]) and self.check_perp([c, d, m, n]):
            return True

        return False

    def check_eqratio(self, points: list[Point]) -> bool:
        """Check if 8 points make an eqratio predicate."""
        a, b, c, d, m, n, p, q = points

        if {a, b} == {c, d} and {m, n} == {p, q}:
            return True
        if {a, b} == {m, n} and {c, d} == {p, q}:
            return True

        ab = self.symbols_graph.get_segment(a, b)
        cd = self.symbols_graph.get_segment(c, d)
        mn = self.symbols_graph.get_segment(m, n)
        pq = self.symbols_graph.get_segment(p, q)

        if {a, b} == {c, d} and mn and pq and is_equal(mn, pq):
            return True
        if {a, b} == {m, n} and cd and pq and is_equal(cd, pq):
            return True
        if {p, q} == {m, n} and ab and cd and is_equal(ab, cd):
            return True
        if {p, q} == {c, d} and ab and mn and is_equal(ab, mn):
            return True

        if not ab or not cd or not mn or not pq:
            return False

        if is_equal(ab, cd) and is_equal(mn, pq):
            return True
        if is_equal(ab, mn) and is_equal(cd, pq):
            return True

        if not (ab.val and cd.val and mn.val and pq.val):
            return False

        if (ab.val, cd.val) == (mn.val, pq.val) or (ab.val, mn.val) == (
            cd.val,
            pq.val,
        ):
            return True

        for rat1, _, _ in all_ratios(ab._val, cd._val):
            for rat2, _, _ in all_ratios(mn._val, pq._val):
                if is_equal(rat1, rat2):
                    return True
        return False

    def check_eqratio3(self, points: list[Point]) -> bool:
        for ratio in list_eqratio3(points):
            if not self.check_eqratio(ratio):
                return False
        return True

    # Algebraic checks

    def check_aconst(self, points: tuple[Point, Point, Point, Point, Angle]) -> bool:
        """Check if the angle is equal to a certain constant."""
        a, b, c, d, angle = points
        num, den = angle_to_num_den(angle)
        ang, _ = self.symbols_graph.get_or_create_const_ang(int(num), int(den))

        ab = self.symbols_graph.get_line(a, b)
        cd = self.symbols_graph.get_line(c, d)
        if not ab or not cd:
            return False

        if not (ab.val and cd.val):
            return False

        for ang1, _, _ in all_angles(ab._val, cd._val):
            if is_equal(ang1, ang):
                return True
        return False

    def check_sangle(self, points: tuple[Point, Point, Point, Angle]) -> bool:
        a, b, c, angle = points
        num, den = angle_to_num_den(angle)
        ang, _ = self.symbols_graph.get_or_create_const_ang(num, den)

        ab = self.symbols_graph.get_line(a, b)
        cb = self.symbols_graph.get_line(c, b)
        if not ab or not cb:
            return False

        if not (ab.val and cb.val):
            return False

        for ang1, _, _ in all_angles(ab._val, cb._val):
            if is_equal(ang1, ang):
                return True
        return False

    def check_rconst(self, points: tuple[Point, Point, Point, Point, Ratio]) -> bool:
        """Check whether a ratio is equal to some given constant."""
        a, b, c, d, ratio = points
        num, den = ratio_to_num_den(ratio)
        rat, _ = self.symbols_graph.get_or_create_const_rat(int(num), int(den))

        ab = self.symbols_graph.get_segment(a, b)
        cd = self.symbols_graph.get_segment(c, d)

        if not ab or not cd:
            return False

        if not (ab.val and cd.val):
            return False

        for rat1, _, _ in all_ratios(ab._val, cd._val):
            if is_equal(rat1, rat):
                return True
        return False

    def check_lconst(self, points: tuple[Point, Point, Length]) -> bool:
        """Check whether a length is equal to some given constant."""
        a, b, length = points
        ab = self.symbols_graph.get_segment(a, b)

        if not ab or not ab.val:
            return False

        for len1, _ in all_lengths(ab):
            if is_equal(len1, length):
                return True
        return False

    def check_acompute(self, points: list[Point]) -> bool:
        """Check if an angle has a constant value."""
        a, b, c, d = points
        ab = self.symbols_graph.get_line(a, b)
        cd = self.symbols_graph.get_line(c, d)
        if not ab or not cd:
            return False

        if not (ab.val and cd.val):
            return False

        for ang0 in self.symbols_graph.aconst.values():
            for ang in ang0.val.neighbors(Angle):
                d1, d2 = ang.directions
                if ab.val == d1 and cd.val == d2:
                    return True
        return False

    def check_rcompute(self, points: list[Point]) -> bool:
        """Check whether a ratio is equal to some constant."""
        a, b, c, d = points
        ab = self.symbols_graph.get_segment(a, b)
        cd = self.symbols_graph.get_segment(c, d)

        if not ab or not cd:
            return False

        if not (ab.val and cd.val):
            return False

        for rat0 in self.symbols_graph.rconst.values():
            for rat in rat0.val.neighbors(Ratio):
                l1, l2 = rat.lengths
                if ab.val == l1 and cd.val == l2:
                    return True
        return False

    # High order checks

    def check_midp(self, points: list[Point]) -> bool:
        if not self.check_coll(points):
            return False
        m, a, b = points
        return self.check_cong([m, a, m, b])

    def check_circle(self, points: list[Point]) -> bool:
        o, a, b, c = points
        return self.check_cong([o, a, o, b]) and self.check_cong([o, a, o, c])

    def check_cyclic(self, points: list[Point]) -> bool:
        points = list(set(points))
        if len(points) < 4:
            return True
        circle2count = defaultdict(lambda: 0)
        for p in points:
            for c in p.neighbors(Circle):
                circle2count[c] += 1
        return any([count == len(points) for _, count in circle2count.items()])

    def check_simtri(self, points: list[Point]) -> bool:
        a, b, c, x, y, z = points
        return self.check_eqangle([a, b, a, c, x, y, x, z]) and self.check_eqangle(
            [b, a, b, c, y, x, y, z]
        )

    def check_simtri_reflected(self, points: list[Point]) -> bool:
        a, b, c, x, y, z = points
        return self.check_eqangle([a, b, a, c, x, z, x, y]) and self.check_eqangle(
            [b, a, b, c, y, z, y, x]
        )

    def check_simtri_both(self, points: list[Point]) -> bool:
        return self.check_simtri(points) or self.check_simtri_reflected(points)

    def check_contri(self, points: list[Point]) -> bool:
        return self.check_contri_both(points) and self.check_simtri(points)

    def check_contri_reflected(self, points: list[Point]) -> bool:
        return self.check_contri_both(points) and self.check_simtri_reflected(points)

    def check_contri_both(self, points: list[Point]) -> bool:
        a, b, c, x, y, z = points
        return (
            self.check_cong([a, b, x, y])
            and self.check_cong([b, c, y, z])
            and self.check_cong([c, a, z, x])
        )

    # Negative checks (with numerical double check)

    def check_ncoll(self, points: list[Point]) -> bool:
        if self.check_coll(points):
            return False
        return not check_coll_numerical([p.num for p in points])

    def check_npara(self, points: list[Point]) -> bool:
        if self.check_para(points):
            return False
        return not check_para_numerical([p.num for p in points])

    def check_nperp(self, points: list[Point]) -> bool:
        if self.check_perp(points):
            return False
        return not check_perp_numerical([p.num for p in points])

    # Numerical only checks

    def check_sameside(self, points: list[Point]) -> bool:
        return check_sameside_numerical([p.num for p in points])

    def check_diff(self, points: list[Point]) -> bool:
        a, b = points
        return not a.num.close(b.num)
