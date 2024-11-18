from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Optional


import newclid.combinatorics as comb
from newclid.statements.statement import Statement, angle_to_num_den, ratio_to_num_den

from newclid.predicates import Predicate
import newclid.numerical.check as nm


from newclid.dependencies.dependency import Reason, Dependency
from newclid.dependencies.dependency_building import DependencyBody
from newclid.geometry import (
    Angle,
    Length,
    Line,
    Symbol,
    Point,
    Segment,
    is_equal,
)
from newclid.listing import list_eqratio3


ToCache = tuple[Statement, Dependency]

if TYPE_CHECKING:
    from newclid.symbols_graph import SymbolsGraph
    from newclid.statements.checker import StatementChecker
    from newclid.dependencies.caching import DependencyCache
    from newclid.dependencies.why_graph import WhyHyperGraph


class IntrinsicRules(Enum):
    PARA_FROM_PERP = "i00"
    CYCLIC_FROM_CONG = "i01"
    CONG_FROM_EQRATIO = "i02"
    PARA_FROM_EQANGLE = "i03"

    POINT_ON_SAME_LINE = "i04"
    PARA_FROM_LINES = "i05"
    PERP_FROM_LINES = "i06"
    PERP_FROM_ANGLE = "i07"
    EQANGLE_FROM_LINES = "i08"
    EQANGLE_FROM_CONGRUENT_ANGLE = "i09"
    EQRATIO_FROM_PROPORTIONAL_SEGMENTS = "i10"
    CYCLIC_FROM_CIRCLE = "i11"

    ACONST_FROM_LINES = "i12"
    ACONST_FROM_ANGLE = "i13"
    SANGLE_FROM_ANGLE = "i14"
    RCONST_FROM_RATIO = "i15"

    PERP_FROM_PARA = "i16"
    EQANGLE_FROM_PARA = "i17"
    EQRATIO_FROM_CONG = "i18"
    ACONST_FROM_PARA = "i19"
    RCONST_FROM_CONG = "i20"

    SANGLE_FROM_LINES = "i21"
    SANGLE_FROM_PARA = "i22"


ALL_INTRINSIC_RULES = [rule for rule in IntrinsicRules]


class SymbolicError(Exception):
    """A symbolic manipulation was wrong"""


class StatementAdder:
    def __init__(
        self,
        symbols_graph: "SymbolsGraph",
        statements_graph: "WhyHyperGraph",
        statements_checker: "StatementChecker",
        dependency_cache: "DependencyCache",
        disabled_intrinsic_rules: Optional[list[IntrinsicRules | str]] = None,
    ) -> None:
        self.symbols_graph = symbols_graph

        self.statements_checker = statements_checker
        self.dependency_cache = dependency_cache
        self.statements_graph = statements_graph

        if disabled_intrinsic_rules is None:
            disabled_intrinsic_rules = []
        self.DISABLED_INTRINSIC_RULES = [
            IntrinsicRules(r) for r in disabled_intrinsic_rules
        ]

        self.PREDICATE_TO_ADDER = {
            Predicate.COLLINEAR: self._add_coll,
            Predicate.COLLINEAR_X: self._add_coll,
            Predicate.PARALLEL: self._add_para,
            Predicate.PERPENDICULAR: self._add_perp,
            Predicate.MIDPOINT: self._add_midp,
            Predicate.CONGRUENT: self._add_cong,
            Predicate.CONGRUENT_2: self._add_cong2,
            Predicate.CIRCLE: self._add_circle,
            Predicate.CYCLIC: self._add_cyclic,
            Predicate.EQANGLE: self._add_eqangle,
            Predicate.EQANGLE6: self._add_eqangle,
            Predicate.S_ANGLE: self._add_s_angle,
            Predicate.EQRATIO: self._add_eqratio,
            Predicate.EQRATIO6: self._add_eqratio,
            Predicate.EQRATIO3: self._add_eqratio3,
            # Predicate.EQRATIO4: self._add_eqratio4,
            Predicate.SIMILAR_TRIANGLE: self._add_simtri,
            Predicate.SIMILAR_TRIANGLE_REFLECTED: self._add_simtri_reflect,
            Predicate.SIMILAR_TRIANGLE_BOTH: self._add_simtri_check,
            Predicate.CONTRI_TRIANGLE: self._add_contri,
            Predicate.CONTRI_TRIANGLE_REFLECTED: self._add_contri_reflect,
            Predicate.CONTRI_TRIANGLE_BOTH: self._add_contri_check,
            Predicate.CONSTANT_ANGLE: self._add_aconst,
            Predicate.CONSTANT_RATIO: self._add_rconst,
            Predicate.CONSTANT_LENGTH: self._add_lconst,
        }

    def add(
        self,
        statement: Statement,
        dep_body: DependencyBody,
        ensure_numerically_sound: bool = False,
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add a new predicate."""
        if ensure_numerically_sound and not nm.check_numerical(statement):
            raise SymbolicError(
                f"Statement {statement} was symbolicaly added "
                f"for reason {dep_body.reason} but is numerically false."
            )
        piece_adder = self.PREDICATE_TO_ADDER.get(statement.predicate)
        if piece_adder is not None:
            return piece_adder(statement.args, dep_body)

        deps_to_cache = []
        # Cached or compute piece
        if statement.predicate in [
            Predicate.COMPUTE_ANGLE,
            Predicate.COMPUTE_RATIO,
            Predicate.FIX_L,
            Predicate.FIX_C,
            Predicate.FIX_B,
            Predicate.FIX_T,
            Predicate.FIX_P,
        ]:
            dep = dep_body.build(self.statements_graph, statement)
            deps_to_cache.append((statement, dep))
            new_deps = [dep]
        elif statement.predicate is Predicate.IND:
            new_deps = []
        else:
            raise ValueError(f"Not recognize predicate {statement.predicate}")

        return new_deps, deps_to_cache

    def _make_equal(self, x: Symbol, y: Symbol, dep: Dependency) -> None:
        """Make that two nodes x and y are equal, i.e. merge their value node."""
        if x.val is None:
            x, y = y, x

        self.symbols_graph.get_node_val(x, dep=None)
        self.symbols_graph.get_node_val(y, dep=None)
        vx = x._val
        vy = y._val

        if vx == vy:
            return

        merges = [vx, vy]

        # If eqangle on the same directions switched then they are perpendicular
        if (
            isinstance(x, Angle)
            and x not in self.symbols_graph.aconst.values()
            and y not in self.symbols_graph.aconst.values()
            and x.directions == y.directions[::-1]
            and x.directions[0] != x.directions[1]
        ):
            merges = [self.symbols_graph.vhalfpi, vx, vy]

        self.symbols_graph.merge(merges, dep)

    def _add_coll(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add a predicate that `points` are collinear."""
        points = list(set(points))
        og_points = points.copy()

        all_lines: list[Line] = []
        for p1, p2 in comb.arrangement_pairs(points):
            all_lines.append(self.symbols_graph.get_line_thru_pair(p1, p2))
        points = sum([line.neighbors(Point) for line in all_lines], [])
        points = list(set(points))

        existed: set[Line] = set()
        new: set[Line] = set()
        for p1, p2 in comb.arrangement_pairs(points):
            if p1.name > p2.name:
                p1, p2 = p2, p1
            if (p1, p2) in self.symbols_graph._pair2line:
                line = self.symbols_graph._pair2line[(p1, p2)]
                existed.add(line)
            else:
                line = self.symbols_graph.get_new_line_thru_pair(p1, p2)
                new.add(line)

        sorted_existed: list[Line] = list(sorted(existed, key=lambda node: node.name))
        sorted_new: list[Line] = list(sorted(new, key=lambda node: node.name))
        if not sorted_existed:
            line0, *lines = sorted_new
        else:
            line0, lines = sorted_existed[0], sorted_existed[1:] + sorted_new

        add = []
        to_cache = []
        line0, why0 = line0.rep_and_why()
        a, b = line0.points
        for line in lines:
            c, d = line.points
            args = list({a, b, c, d})
            if len(args) < 3:
                continue

            whys: list[Dependency] = []
            for x in args:
                if x not in og_points:
                    whys.append(self._coll_dep(og_points, x))

            abcd_deps = dep_body
            if IntrinsicRules.POINT_ON_SAME_LINE not in self.DISABLED_INTRINSIC_RULES:
                abcd_deps = dep_body.extend_by_why(
                    self.statements_graph,
                    Statement(Predicate.COLLINEAR, og_points),
                    why=whys + why0,
                    extention_reason=Reason(IntrinsicRules.POINT_ON_SAME_LINE),
                )

            is_coll = self.statements_checker.check_coll(args)
            coll = Statement(Predicate.COLLINEAR, args)
            dep = abcd_deps.build(self.statements_graph, coll)
            to_cache.append((coll, dep))
            self.symbols_graph.merge_into(line0, [line], dep)

            if not is_coll:
                add += [dep]

        return add, to_cache

    def _coll_dep(self, points: list[Point], p: Point) -> list[Dependency]:
        """Return the dep(.why) explaining why p is coll with points."""
        for p1, p2 in comb.arrangement_pairs(points):
            if self.statements_checker.check_coll([p1, p2, p]):
                coll = Statement(Predicate.COLLINEAR, (p1, p2, p))
                return self.statements_graph.build_resolved_dependency(coll)

    def _add_para(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add a new predicate that 4 points (2 lines) are parallel."""
        a, b, c, d = points
        ab, why1 = self.symbols_graph.get_line_thru_pair_why(a, b)
        cd, why2 = self.symbols_graph.get_line_thru_pair_why(c, d)

        (a, b), (c, d) = ab.points, cd.points

        if IntrinsicRules.PARA_FROM_LINES not in self.DISABLED_INTRINSIC_RULES:
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                Statement(Predicate.PARALLEL, points),
                why=why1 + why2,
                extention_reason=Reason(IntrinsicRules.PARA_FROM_LINES),
            )

        para = Statement(Predicate.PARALLEL, (a, b, c, d))
        dep = dep_body.build(self.statements_graph, para)
        to_cache = [(para, dep)]

        self._make_equal(ab, cd, dep)
        if not is_equal(ab, cd):
            return [dep], to_cache
        return [], to_cache

    def _add_para_or_coll_from_perp(
        self,
        a: Point,
        b: Point,
        c: Point,
        d: Point,
        x: Point,
        y: Point,
        m: Point,
        n: Point,
        dep_body: DependencyBody,
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add a new parallel or collinear predicate."""
        perp = Statement(Predicate.PERPENDICULAR, [a, b, c, d])
        extends = [Statement(Predicate.PERPENDICULAR, [x, y, m, n])]
        if {a, b} == {x, y}:
            pass
        elif self.statements_checker.check_para([a, b, x, y]):
            extends.append(Statement(Predicate.PARALLEL, [a, b, x, y]))
        elif self.statements_checker.check_coll([a, b, x, y]):
            extends.append(Statement(Predicate.COLLINEAR, set(list([a, b, x, y]))))
        else:
            return None

        if m in [c, d] or n in [c, d] or c in [m, n] or d in [m, n]:
            pass
        elif self.statements_checker.check_coll([c, d, m]):
            extends.append(Statement(Predicate.COLLINEAR, [c, d, m]))
        elif self.statements_checker.check_coll([c, d, n]):
            extends.append(Statement(Predicate.COLLINEAR, [c, d, n]))
        elif self.statements_checker.check_coll([c, m, n]):
            extends.append(Statement(Predicate.COLLINEAR, [c, m, n]))
        elif self.statements_checker.check_coll([d, m, n]):
            extends.append(Statement(Predicate.COLLINEAR, [d, m, n]))
        else:
            dep_body = dep_body.extend_many(
                self.statements_graph,
                perp,
                extends,
                extention_reason=Reason(IntrinsicRules.PARA_FROM_PERP),
            )
            return self._add_para([c, d, m, n], dep_body)

        dep_body = dep_body.extend_many(
            self.statements_graph,
            perp,
            extends,
            extention_reason=Reason(IntrinsicRules.PARA_FROM_PERP),
        )
        return self._add_coll(list(set([c, d, m, n])), dep_body)

    def _maybe_make_para_from_perp(
        self, points: list[Point], dep_body: DependencyBody
    ) -> Optional[tuple[list[Dependency], list[ToCache]]]:
        """Maybe add a new parallel predicate from perp predicate."""
        a, b, c, d = points
        halfpi = self.symbols_graph.aconst[(1, 2)]
        for ang in halfpi.val.neighbors(Angle):
            if ang == halfpi:
                continue
            d1, d2 = ang.directions
            x, y = d1._obj.points
            m, n = d2._obj.points

            for args in [
                (a, b, c, d, x, y, m, n),
                (a, b, c, d, m, n, x, y),
                (c, d, a, b, x, y, m, n),
                (c, d, a, b, m, n, x, y),
            ]:
                para_or_coll = self._add_para_or_coll_from_perp(*args, dep_body)
                if para_or_coll is not None:
                    return para_or_coll

        return None

    def _add_perp(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add a new perpendicular predicate from 4 points (2 lines)."""

        if IntrinsicRules.PARA_FROM_PERP not in self.DISABLED_INTRINSIC_RULES:
            para_from_perp = self._maybe_make_para_from_perp(points, dep_body)
            if para_from_perp is not None:
                return para_from_perp

        a, b, c, d = points
        ab, why1 = self.symbols_graph.get_line_thru_pair_why(a, b)
        cd, why2 = self.symbols_graph.get_line_thru_pair_why(c, d)

        (a, b), (c, d) = ab.points, cd.points

        if IntrinsicRules.PERP_FROM_LINES not in self.DISABLED_INTRINSIC_RULES:
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                Statement(Predicate.PERPENDICULAR, points),
                extention_reason=Reason(IntrinsicRules.PERP_FROM_LINES),
                why=why1 + why2,
            )

        self.symbols_graph.get_node_val(ab, dep=None)
        self.symbols_graph.get_node_val(cd, dep=None)

        if ab.val == cd.val:
            raise ValueError(f"{ab.name} and {cd.name} Cannot be perp.")

        args = [a, b, c, d]
        i = 0
        for x, y, xy in [(a, b, ab), (c, d, cd)]:
            i += 1
            x_, y_ = xy._val._obj.points
            if {x, y} == {x_, y_}:
                continue
            if (
                dep_body
                and IntrinsicRules.PERP_FROM_PARA not in self.DISABLED_INTRINSIC_RULES
            ):
                perp = Statement(Predicate.PERPENDICULAR, list(args))
                para = Statement(Predicate.PARALLEL, [x, y, x_, y_])
                dep_body = dep_body.extend(
                    self.statements_graph,
                    perp,
                    para,
                    extention_reason=Reason(IntrinsicRules.PERP_FROM_PARA),
                )
            args[2 * i - 2] = x_
            args[2 * i - 1] = y_

        a12, a21, why = self.symbols_graph.get_or_create_angle_from_lines(
            ab, cd, dep=None
        )

        perp = Statement(Predicate.PERPENDICULAR, [a, b, c, d])
        if IntrinsicRules.PERP_FROM_ANGLE not in self.DISABLED_INTRINSIC_RULES:
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                perp,
                why=why,
                extention_reason=Reason(IntrinsicRules.PERP_FROM_ANGLE),
            )

        dab, dcd = a12._d
        a, b = dab._obj.points
        c, d = dcd._obj.points

        dep = dep_body.build(self.statements_graph, perp)
        was_already_equal = is_equal(a12, a21)
        self._make_equal(a12, a21, dep=dep)

        eqangle = Statement(Predicate.EQANGLE, [a, b, c, d, c, d, a, b])
        to_cache = [(perp, dep), (eqangle, dep)]

        if not was_already_equal:
            return [dep], to_cache
        return [], to_cache

    def _add_cong(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add that two segments (4 points) are congruent."""
        a, b, c, d = points
        ab = self.symbols_graph.get_or_create_segment(a, b, None)
        cd = self.symbols_graph.get_or_create_segment(c, d, None)

        cong = Statement(Predicate.CONGRUENT, [a, b, c, d])
        dep = dep_body.build(self.statements_graph, cong)
        self._make_equal(ab, cd, dep=dep)

        to_cache = [(cong, dep)]
        added = []

        if not is_equal(ab, cd):
            added += [dep]

        if IntrinsicRules.CYCLIC_FROM_CONG in self.DISABLED_INTRINSIC_RULES or (
            a not in [c, d] and b not in [c, d]
        ):
            return added, to_cache

        # Make a=c if possible
        if b in [c, d]:
            a, b = b, a
        if a == d:
            c, d = d, c

        cyclic_deps, cyclic_cache = self._maybe_add_cyclic_from_cong(a, b, d, dep)
        added += cyclic_deps
        to_cache += cyclic_cache
        return added, to_cache

    def _add_cong2(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        m, n, a, b = points
        add, to_cache = self._add_cong([m, a, n, a], dep_body)
        _add, _to_cache = self._add_cong([m, b, n, b], dep_body)
        return add + _add, to_cache + _to_cache

    def _add_midp(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        m, a, b = points
        add_coll, to_cache_coll = self._add_coll(points, dep_body)
        add_cong, to_cache_cong = self._add_cong([m, a, m, b], dep_body)
        return add_coll + add_cong, to_cache_coll + to_cache_cong

    def _add_circle(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        o, a, b, c = points
        add_ab, to_cache_ab = self._add_cong([o, a, o, b], dep_body)
        add_ac, to_cache_ac = self._add_cong([o, a, o, c], dep_body)
        return add_ab + add_ac, to_cache_ab + to_cache_ac

    def _add_cyclic(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add a new cyclic predicate that 4 points are concyclic."""
        points = list(set(points))
        og_points = list(points)

        all_circles = []
        for p1, p2, p3 in comb.arrangement_triplets(points):
            all_circles.append(self.symbols_graph.get_circle_thru_triplet(p1, p2, p3))
        points = sum([c.neighbors(Point) for c in all_circles], [])
        points = list(set(points))

        existed = set()
        new = set()
        for p1, p2, p3 in comb.arrangement_triplets(points):
            p1, p2, p3 = sorted([p1, p2, p3], key=lambda x: x.name)

            if (p1, p2, p3) in self.symbols_graph._triplet2circle:
                circle = self.symbols_graph._triplet2circle[(p1, p2, p3)]
                existed.add(circle)
            else:
                circle = self.symbols_graph.get_new_circle_thru_triplet(p1, p2, p3)
                new.add(circle)

        existed = sorted(existed, key=lambda node: node.name)
        new = sorted(new, key=lambda node: node.name)

        existed, new = list(existed), list(new)
        if not existed:
            circle0, *circles = new
        else:
            circle0, circles = existed[0], existed[1:] + new

        add = []
        to_cache = []
        circle0, why0 = circle0.rep_and_why()
        a, b, c = circle0.points
        for circle in circles:
            d, e, f = circle.points
            args = list({a, b, c, d, e, f})
            if len(args) < 4:
                continue
            whys = []
            for x in [a, b, c, d, e, f]:
                if x not in og_points:
                    whys.append(self._cyclic_dep(og_points, x))

            abcdef_deps = dep_body
            if IntrinsicRules.CYCLIC_FROM_CIRCLE:
                cyclic = Statement(Predicate.CYCLIC, og_points)
                abcdef_deps = abcdef_deps.extend_by_why(
                    self.statements_graph,
                    cyclic,
                    why=whys + why0,
                    extention_reason=Reason(IntrinsicRules.CYCLIC_FROM_CIRCLE),
                )

            is_cyclic = self.statements_checker.check_cyclic(args)

            cyclic = Statement(Predicate.CYCLIC, args)
            dep = abcdef_deps.build(self.statements_graph, cyclic)
            to_cache.append((cyclic, dep))
            self.symbols_graph.merge_into(circle0, [circle], dep)
            if not is_cyclic:
                add += [dep]

        return add, to_cache

    def _cyclic_dep(self, points: list[Point], p: Point) -> list[Dependency]:
        for p1, p2, p3 in comb.arrangement_triplets(points):
            if self.statements_checker.check_cyclic([p1, p2, p3, p]):
                cyclic = Statement(Predicate.CYCLIC, (p1, p2, p3, p))
                return self.statements_graph.build_resolved_dependency(cyclic)

    def _maybe_add_cyclic_from_cong(
        self, a: Point, b: Point, c: Point, cong_ab_ac: Dependency
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Maybe add a new cyclic predicate from given congruent segments."""
        ab = self.symbols_graph.get_or_create_segment(a, b, None)

        # all eq segs with one end being a.
        segs = [s for s in ab.val.neighbors(Segment) if a in s.points]

        # all points on circle (a, b)
        points = []
        for s in segs:
            x, y = list(s.points)
            points.append(x if y == a else y)

        # for sure both b and c are in points
        points = [p for p in points if p not in [b, c]]

        if len(points) < 2:
            return [], []

        x, y = points[:2]

        if self.statements_checker.check_cyclic([b, c, x, y]):
            return [], []

        ax = self.symbols_graph.get_or_create_segment(a, x, dep=None)
        ay = self.symbols_graph.get_or_create_segment(a, y, dep=None)
        why = ab._val.why_equal([ax._val, ay._val])
        why += [cong_ab_ac]

        dep_body = DependencyBody(Reason(IntrinsicRules.CYCLIC_FROM_CONG), why=why)
        return self._add_cyclic([b, c, x, y], dep_body)

    def _add_eqangle(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add eqangle made by 8 points in `points`."""
        if dep_body:
            dep_body = dep_body.copy()
        a, b, c, d, m, n, p, q = points
        ab, why1 = self.symbols_graph.get_line_thru_pair_why(a, b)
        cd, why2 = self.symbols_graph.get_line_thru_pair_why(c, d)
        mn, why3 = self.symbols_graph.get_line_thru_pair_why(m, n)
        pq, why4 = self.symbols_graph.get_line_thru_pair_why(p, q)

        a, b = ab.points
        c, d = cd.points
        m, n = mn.points
        p, q = pq.points

        if IntrinsicRules.EQANGLE_FROM_LINES not in self.DISABLED_INTRINSIC_RULES:
            eqangle = Statement(Predicate.EQANGLE, points)
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                eqangle,
                why=why1 + why2 + why3 + why4,
                extention_reason=Reason(IntrinsicRules.EQANGLE_FROM_LINES),
            )

        if IntrinsicRules.PARA_FROM_EQANGLE not in self.DISABLED_INTRINSIC_RULES:
            maybe_pairs = self._maybe_make_equal_pairs(
                a, b, c, d, m, n, p, q, ab, cd, mn, pq, dep_body
            )
            if maybe_pairs is not None:
                return maybe_pairs

        self.symbols_graph.get_node_val(ab, dep=None)
        self.symbols_graph.get_node_val(cd, dep=None)
        self.symbols_graph.get_node_val(mn, dep=None)
        self.symbols_graph.get_node_val(pq, dep=None)

        add, to_cache = [], []

        if (
            ab.val != cd.val
            and mn.val != pq.val
            and (ab.val != mn.val or cd.val != pq.val)
        ):
            _add, _to_cache = self._add_eqangle8(
                a, b, c, d, m, n, p, q, ab, cd, mn, pq, dep_body
            )
            add += _add
            to_cache += _to_cache

        if (
            ab.val != mn.val
            and cd.val != pq.val
            and (ab.val != cd.val or mn.val != pq.val)
        ):
            _add, _to_cache = self._add_eqangle8(
                a, b, m, n, c, d, p, q, ab, mn, cd, pq, dep_body
            )
            add += _add
            to_cache += _to_cache

        return add, to_cache

    def _add_eqangle8(
        self,
        a: Point,
        b: Point,
        c: Point,
        d: Point,
        m: Point,
        n: Point,
        p: Point,
        q: Point,
        ab: Line,
        cd: Line,
        mn: Line,
        pq: Line,
        dep_body: DependencyBody,
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add eqangle core."""
        if dep_body:
            dep_body = dep_body.copy()

        args = [a, b, c, d, m, n, p, q]
        i = 0
        for x, y, xy in [(a, b, ab), (c, d, cd), (m, n, mn), (p, q, pq)]:
            i += 1
            x_, y_ = xy._val._obj.points
            if {x, y} == {x_, y_}:
                continue
            if (
                dep_body
                and IntrinsicRules.EQANGLE_FROM_PARA
                not in self.DISABLED_INTRINSIC_RULES
            ):
                eqangle = Statement(Predicate.EQANGLE, tuple(args))
                para = Statement(Predicate.PARALLEL, [x, y, x_, y_])
                dep_body = dep_body.extend(
                    self.statements_graph,
                    eqangle,
                    para,
                    extention_reason=Reason(IntrinsicRules.EQANGLE_FROM_PARA),
                )
                args[2 * i - 2] = x_
                args[2 * i - 1] = y_

        ab_cd, cd_ab, why1 = self.symbols_graph.get_or_create_angle_from_lines(
            ab, cd, dep=None
        )
        mn_pq, pq_mn, why2 = self.symbols_graph.get_or_create_angle_from_lines(
            mn, pq, dep=None
        )

        if (
            IntrinsicRules.EQANGLE_FROM_CONGRUENT_ANGLE
            not in self.DISABLED_INTRINSIC_RULES
        ):
            eqangle = Statement(Predicate.EQANGLE, args)
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                eqangle,
                why=why1 + why2,
                extention_reason=Reason(IntrinsicRules.EQANGLE_FROM_CONGRUENT_ANGLE),
            )

        dab, dcd = ab_cd._d
        dmn, dpq = mn_pq._d

        a, b = dab._obj.points
        c, d = dcd._obj.points
        m, n = dmn._obj.points
        p, q = dpq._obj.points

        add = []
        to_cache = []

        dep1 = None
        eqangle = Statement(Predicate.EQANGLE, [a, b, c, d, m, n, p, q])
        if dep_body:
            dep1 = dep_body.build(self.statements_graph, eqangle)
        if not is_equal(ab_cd, mn_pq):
            add += [dep1]
        to_cache.append((eqangle, dep1))
        self._make_equal(ab_cd, mn_pq, dep=dep1)

        dep2 = None
        eqangle_sym = Statement(Predicate.EQANGLE, [c, d, a, b, p, q, m, n])
        if dep_body:
            dep2 = dep_body.build(self.statements_graph, eqangle_sym)
        if not is_equal(cd_ab, pq_mn):
            add += [dep2]
        to_cache.append((eqangle_sym, dep2))
        self._make_equal(cd_ab, pq_mn, dep=dep2)

        return add, to_cache

    def _add_eqratio3(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add three eqratios through a list of 6 points (due to parallel lines).

          a -- b
         m ---- n
        c ------ d

        """
        add, to_cache = [], []
        ratios = list_eqratio3(points)
        for ratio_points in ratios:
            _add, _to_cache = self._add_eqratio(ratio_points, dep_body)
            add += _add
            to_cache += _to_cache

        self._simple_add(Predicate.EQRATIO3, tuple(points), dep_body, add, to_cache)
        return add, to_cache

    def _add_eqratio4(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add four eqratios through a list of 5 points
            (due to parallel lines with common point).

           o
         a - b
        c --- d

        """
        o, a, b, c, d = points
        add, to_cache = self._add_eqratio3([a, b, c, d, o, o], dep_body)
        _add, _to_cache = self._add_eqratio([o, a, o, c, a, b, c, d], dep_body)
        return add + _add, to_cache + _to_cache

    def _add_eqratio(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add a new eqratio from 8 points."""
        if dep_body:
            dep_body = dep_body.copy()
        a, b, c, d, m, n, p, q = points
        ab = self.symbols_graph.get_or_create_segment(a, b, dep=None)
        cd = self.symbols_graph.get_or_create_segment(c, d, dep=None)
        mn = self.symbols_graph.get_or_create_segment(m, n, dep=None)
        pq = self.symbols_graph.get_or_create_segment(p, q, dep=None)

        if IntrinsicRules.CONG_FROM_EQRATIO not in self.DISABLED_INTRINSIC_RULES:
            add = self._maybe_make_equal_pairs(
                a, b, c, d, m, n, p, q, ab, cd, mn, pq, dep_body
            )
            if add is not None:
                return add

        self.symbols_graph.get_node_val(ab, dep=None)
        self.symbols_graph.get_node_val(cd, dep=None)
        self.symbols_graph.get_node_val(mn, dep=None)
        self.symbols_graph.get_node_val(pq, dep=None)

        add = []
        to_cache = []
        if (
            ab.val != cd.val
            and mn.val != pq.val
            and (ab.val != mn.val or cd.val != pq.val)
        ):
            _add, _to_cache = self._add_eqratio8(
                a, b, c, d, m, n, p, q, ab, cd, mn, pq, dep_body
            )
            add += _add
            to_cache += _to_cache

        if (
            ab.val != mn.val
            and cd.val != pq.val
            and (ab.val != cd.val or mn.val != pq.val)
        ):
            _add, _to_cache = self._add_eqratio8(
                a, b, m, n, c, d, p, q, ab, mn, cd, pq, dep_body
            )
            add += _add
            to_cache += _to_cache
        return add, to_cache

    def _add_eqratio8(
        self,
        a: Point,
        b: Point,
        c: Point,
        d: Point,
        m: Point,
        n: Point,
        p: Point,
        q: Point,
        ab: Segment,
        cd: Segment,
        mn: Segment,
        pq: Segment,
        dep_body: DependencyBody,
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add a new eqratio from 8 points (core)."""
        if dep_body:
            dep_body = dep_body.copy()

        args = [a, b, c, d, m, n, p, q]
        i = 0
        for x, y, xy in [(a, b, ab), (c, d, cd), (m, n, mn), (p, q, pq)]:
            if {x, y} == set(xy.points):
                continue
            x_, y_ = list(xy.points)
            if (
                dep_body
                and IntrinsicRules.EQRATIO_FROM_CONG
                not in self.DISABLED_INTRINSIC_RULES
            ):
                eqratio = Statement(Predicate.EQRATIO, tuple(args))
                cong = Statement(Predicate.CONGRUENT, [x, y, x_, y_])
                dep_body = dep_body.extend(
                    self.statements_graph,
                    eqratio,
                    cong,
                    extention_reason=Reason(IntrinsicRules.EQRATIO_FROM_CONG),
                )
            args[2 * i - 2] = x_
            args[2 * i - 1] = y_

        add = []
        ab_cd, cd_ab, why1 = self.symbols_graph.get_or_create_ratio_from_segments(
            ab, cd, dep=None
        )
        mn_pq, pq_mn, why2 = self.symbols_graph.get_or_create_ratio_from_segments(
            mn, pq, dep=None
        )

        if (
            IntrinsicRules.EQRATIO_FROM_PROPORTIONAL_SEGMENTS
            not in self.DISABLED_INTRINSIC_RULES
        ):
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                Statement(Predicate.EQRATIO, tuple(args)),
                why=why1 + why2,
                extention_reason=Reason(
                    IntrinsicRules.EQRATIO_FROM_PROPORTIONAL_SEGMENTS
                ),
            )

        lab, lcd = ab_cd._l
        lmn, lpq = mn_pq._l

        a, b = lab._obj.points
        c, d = lcd._obj.points
        m, n = lmn._obj.points
        p, q = lpq._obj.points

        to_cache = []

        dep1 = None
        eqratio = Statement(Predicate.EQRATIO, [a, b, c, d, m, n, p, q])
        dep1 = dep_body.build(self.statements_graph, eqratio)
        if not is_equal(ab_cd, mn_pq):
            add += [dep1]
        to_cache.append((eqratio, dep1))
        self._make_equal(ab_cd, mn_pq, dep=dep1)

        dep2 = None
        eqratio_sym = Statement(Predicate.EQRATIO, [c, d, a, b, p, q, m, n])
        dep2 = dep_body.build(self.statements_graph, eqratio_sym)
        if not is_equal(cd_ab, pq_mn):
            add += [dep2]
        to_cache.append((eqratio_sym, dep2))
        self._make_equal(cd_ab, pq_mn, dep=dep2)
        return add, to_cache

    def _simple_add(
        self,
        predicate: Predicate,
        points: tuple[Point, ...],
        dep_body: DependencyBody,
        added: list[Dependency],
        to_cache: list[ToCache],
    ):
        statement = Statement(predicate, points)
        dep = self.statements_graph.build_dependency(statement, dep_body)
        added.append(dep)
        to_cache.append((statement, dep))

    def _add_simtri_check(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        if nm.same_clock(*[p.num for p in points]):
            added, to_cache = self._add_simtri(points, dep_body)
        else:
            added, to_cache = self._add_simtri_reflect(points, dep_body)
        self._simple_add(
            Predicate.SIMILAR_TRIANGLE_BOTH, tuple(points), dep_body, added, to_cache
        )
        return added, to_cache

    def _add_contri_check(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        if nm.same_clock(*[p.num for p in points]):
            added, to_cache = self._add_contri(points, dep_body)
        else:
            added, to_cache = self._add_contri_reflect(points, dep_body)
        self._simple_add(
            Predicate.CONTRI_TRIANGLE_BOTH, points, dep_body, added, to_cache
        )
        return added, to_cache

    def _add_simtri(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add two similar triangles."""
        add, to_cache = [], []
        hashs = [dep.statement.hash_tuple for dep in dep_body.why]

        for args in comb.enum_triangle(points):
            eqangle6 = Statement(Predicate.EQANGLE6, args)
            if eqangle6.hash_tuple in hashs:
                continue
            _add, _to_cache = self._add_eqangle(args, dep_body=dep_body)
            add += _add
            to_cache += _to_cache

        for args in comb.enum_triangle(points):
            eqratio6 = Statement(Predicate.EQRATIO6, args)
            if eqratio6.hash_tuple in hashs:
                continue
            _add, _to_cache = self._add_eqratio(args, dep_body=dep_body)
            add += _add
            to_cache += _to_cache

        self._simple_add(
            Predicate.SIMILAR_TRIANGLE, tuple(points), dep_body, add, to_cache
        )
        return add, to_cache

    def _add_simtri_reflect(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add two similar reflected triangles."""
        add, to_cache = [], []
        hashs = [dep.statement.hash_tuple for dep in dep_body.why]
        for args in comb.enum_triangle_reflect(points):
            eqangle6 = Statement(Predicate.EQANGLE6, args)
            if eqangle6.hash_tuple in hashs:
                continue
            _add, _to_cache = self._add_eqangle(args, dep_body=dep_body)
            add += _add
            to_cache += _to_cache

        for args in comb.enum_triangle(points):
            eqratio6 = Statement(Predicate.EQRATIO6, args)
            if eqratio6.hash_tuple in hashs:
                continue
            _add, _to_cache = self._add_eqratio(args, dep_body=dep_body)
            add += _add
            to_cache += _to_cache

        self._simple_add(
            Predicate.SIMILAR_TRIANGLE_REFLECTED,
            tuple(points),
            dep_body,
            add,
            to_cache,
        )
        return add, to_cache

    def _add_contri(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add two congruent triangles."""
        add, to_cache = [], []
        hashs = [dep.statement.hash_tuple for dep in dep_body.why]
        for args in comb.enum_triangle(points):
            eqangle6 = Statement(Predicate.EQANGLE6, args)
            if eqangle6.hash_tuple in hashs:
                continue
            _add, _to_cache = self._add_eqangle(args, dep_body=dep_body)
            add += _add
            to_cache += _to_cache

        for args in comb.enum_sides(points):
            cong = Statement(Predicate.CONGRUENT, args)
            if cong.hash_tuple in hashs:
                continue
            _add, _to_cache = self._add_cong(args, dep_body)
            add += _add
            to_cache += _to_cache

        self._simple_add(
            Predicate.CONTRI_TRIANGLE, tuple(points), dep_body, add, to_cache
        )
        return add, to_cache

    def _add_contri_reflect(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add two congruent reflected triangles."""
        add, to_cache = [], []
        hashs = [dep.statement.hash_tuple for dep in dep_body.why]
        for args in comb.enum_triangle_reflect(points):
            eqangle6 = Statement(Predicate.EQANGLE6, args)
            if eqangle6.hash_tuple in hashs:
                continue
            _add, _to_cache = self._add_eqangle(args, dep_body)
            add += _add
            to_cache += _to_cache

        for args in comb.enum_sides(points):
            cong = Statement(Predicate.CONGRUENT, args)
            if cong.hash_tuple in hashs:
                continue
            _add, _to_cache = self._add_cong(args, dep_body)
            add += _add
            to_cache += _to_cache

        self._simple_add(
            Predicate.CONTRI_TRIANGLE_REFLECTED,
            tuple(points),
            dep_body,
            add,
            to_cache,
        )
        return add, to_cache

    def _maybe_make_equal_pairs(
        self,
        a: Point,
        b: Point,
        c: Point,
        d: Point,
        m: Point,
        n: Point,
        p: Point,
        q: Point,
        ab: Line,
        cd: Line,
        mn: Line,
        pq: Line,
        dep_body: DependencyBody,
    ) -> Optional[tuple[list[Dependency], list[ToCache]]]:
        """Add ab/cd = mn/pq in case maybe either two of (ab,cd,mn,pq) are equal."""
        if is_equal(ab, cd):
            return self._make_equal_pairs(
                a, b, c, d, m, n, p, q, ab, cd, mn, pq, dep_body
            )
        elif is_equal(mn, pq):
            return self._make_equal_pairs(
                m, n, p, q, a, b, c, d, mn, pq, ab, cd, dep_body
            )
        elif is_equal(ab, mn):
            return self._make_equal_pairs(
                a, b, m, n, c, d, p, q, ab, mn, cd, pq, dep_body
            )
        elif is_equal(cd, pq):
            return self._make_equal_pairs(
                c, d, p, q, a, b, m, n, cd, pq, ab, mn, dep_body
            )
        else:
            return None

    def _make_equal_pairs(
        self,
        a: Point,
        b: Point,
        c: Point,
        d: Point,
        m: Point,
        n: Point,
        p: Point,
        q: Point,
        ab: Line,
        cd: Line,
        mn: Line,
        pq: Line,
        dep_body: DependencyBody,
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add ab/cd = mn/pq in case either two of (ab,cd,mn,pq) are equal."""
        if isinstance(ab, Segment):
            dep_pred = Predicate.EQRATIO
            eq_pred = Predicate.CONGRUENT
            intrinsic_rule = IntrinsicRules.CONG_FROM_EQRATIO
        else:
            dep_pred = Predicate.EQANGLE
            eq_pred = Predicate.PARALLEL
            intrinsic_rule = IntrinsicRules.PARA_FROM_EQANGLE

        reason = Reason(intrinsic_rule)
        eq = Statement(dep_pred, [a, b, c, d, m, n, p, q])
        if ab != cd:
            because_eq = Statement(eq_pred, [a, b, c, d])
            dep_body = dep_body.extend(self.statements_graph, eq, because_eq, reason)

        elif eq_pred is Predicate.PARALLEL:  # ab == cd.
            colls = [a, b, c, d]
            if len(set(colls)) > 2:
                because_collx = Statement(Predicate.COLLINEAR_X, colls)
                dep_body = dep_body.extend(
                    self.statements_graph, eq, because_collx, reason
                )

        because_eq = Statement(eq_pred, [m, n, p, q])
        dep = dep_body.build(self.statements_graph, because_eq)
        self._make_equal(mn, pq, dep=dep)

        to_cache = [(because_eq, dep)]

        if is_equal(mn, pq):
            return [], to_cache
        return [dep], to_cache

    def _add_aconst(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add that an angle is equal to some constant."""
        points = list(points)
        a, b, c, d, ang = points

        num, den = angle_to_num_den(ang)
        nd, dn = self.symbols_graph.get_or_create_const_ang(num, den)

        if nd == self.symbols_graph.halfpi:
            return self._add_perp([a, b, c, d], dep_body)

        ab, why1 = self.symbols_graph.get_line_thru_pair_why(a, b)
        cd, why2 = self.symbols_graph.get_line_thru_pair_why(c, d)

        (a, b), (c, d) = ab.points, cd.points
        if IntrinsicRules.ACONST_FROM_LINES not in self.DISABLED_INTRINSIC_RULES:
            args = points[:-1] + [nd]
            aconst = Statement(Predicate.CONSTANT_ANGLE, tuple(args))
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                aconst,
                why=why1 + why2,
                extention_reason=Reason(IntrinsicRules.ACONST_FROM_LINES),
            )

        self.symbols_graph.get_node_val(ab, dep=None)
        self.symbols_graph.get_node_val(cd, dep=None)

        if ab.val == cd.val:
            raise ValueError(f"{ab.name} - {cd.name} cannot be {nd.name}")

        args = [a, b, c, d, nd]
        i = 0
        for x, y, xy in [(a, b, ab), (c, d, cd)]:
            i += 1
            x_, y_ = xy._val._obj.points
            if {x, y} == {x_, y_}:
                continue
            if (
                dep_body
                and IntrinsicRules.ACONST_FROM_PARA not in self.DISABLED_INTRINSIC_RULES
            ):
                aconst = Statement(Predicate.CONSTANT_ANGLE, tuple(args))
                para = Statement(Predicate.PARALLEL, [x, y, x_, y_])
                dep_body = dep_body.extend(
                    self.statements_graph,
                    aconst,
                    para,
                    Reason(IntrinsicRules.ACONST_FROM_PARA),
                )
            args[2 * i - 2] = x_
            args[2 * i - 1] = y_

        ab_cd, cd_ab, why = self.symbols_graph.get_or_create_angle_from_lines(
            ab, cd, dep=None
        )

        aconst = Statement(Predicate.CONSTANT_ANGLE, [a, b, c, d, nd])
        if IntrinsicRules.ACONST_FROM_ANGLE not in self.DISABLED_INTRINSIC_RULES:
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                aconst,
                why=why,
                extention_reason=Reason(IntrinsicRules.ACONST_FROM_ANGLE),
            )

        dab, dcd = ab_cd._d
        a, b = dab._obj.points
        c, d = dcd._obj.points

        ang = int(num) * 180 / int(den)
        add = []
        to_cache = []
        if not is_equal(ab_cd, nd):
            dep1 = dep_body.build(self.statements_graph, aconst)
            self._make_equal(ab_cd, nd, dep=dep1)
            to_cache.append((aconst, dep1))
            add += [dep1]

        aconst2 = Statement(Predicate.CONSTANT_ANGLE, [a, b, c, d, nd])
        if not is_equal(cd_ab, dn):
            dep2 = dep_body.build(self.statements_graph, aconst2)
            self._make_equal(cd_ab, dn, dep=dep2)
            to_cache.append((aconst2, dep2))
            add += [dep2]

        return add, to_cache

    def _add_s_angle(
        self, points: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add that an angle abx is equal to constant y."""
        a, b, x, angle = points
        num, den = angle_to_num_den(angle)
        nd, dn = self.symbols_graph.get_or_create_const_ang(num, den)

        if nd == self.symbols_graph.halfpi:
            return self._add_perp([a, b, b, x], dep_body)

        ab, why1 = self.symbols_graph.get_line_thru_pair_why(a, b)
        bx, why2 = self.symbols_graph.get_line_thru_pair_why(b, x)

        self.symbols_graph.get_node_val(ab, dep=None)
        self.symbols_graph.get_node_val(bx, dep=None)

        add, to_cache = [], []

        if ab.val == bx.val:
            return add, to_cache

        sangle = Statement(Predicate.S_ANGLE, (a, b, x))
        if IntrinsicRules.SANGLE_FROM_LINES not in self.DISABLED_INTRINSIC_RULES:
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                sangle,
                why=why1 + why2,
                extention_reason=Reason(IntrinsicRules.SANGLE_FROM_LINES),
            )

        if IntrinsicRules.SANGLE_FROM_PARA not in self.DISABLED_INTRINSIC_RULES:
            paras = []
            for p, q, pq in [(a, b, ab), (b, x, bx)]:
                p_, q_ = pq.val._obj.points
                if {p, q} == {p_, q_}:
                    continue
                paras.append(Statement(Predicate.PARALLEL, (p, q, p_, q_)))
            if paras:
                dep_body = dep_body.extend_many(
                    self.statements_graph,
                    sangle,
                    paras,
                    Reason(IntrinsicRules.SANGLE_FROM_PARA),
                )

        xba, abx, why = self.symbols_graph.get_or_create_angle_from_lines(
            bx, ab, dep=None
        )
        if IntrinsicRules.SANGLE_FROM_ANGLE not in self.DISABLED_INTRINSIC_RULES:
            aconst = Statement(Predicate.CONSTANT_ANGLE, [b, x, a, b, nd])
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                aconst,
                why=why,
                extention_reason=Reason(IntrinsicRules.SANGLE_FROM_ANGLE),
            )

        dab, dbx = abx._d
        a, b = dab._obj.points
        c, x = dbx._obj.points

        if not is_equal(xba, nd):
            aconst = Statement(Predicate.S_ANGLE, [c, x, a, b, nd])
            dep1 = dep_body.build(self.statements_graph, aconst)
            self._make_equal(xba, nd, dep=dep1)
            to_cache.append((aconst, dep1))
            add += [dep1]

        if not is_equal(abx, dn):
            aconst2 = Statement(Predicate.S_ANGLE, [a, b, c, x, dn])
            dep2 = dep_body.build(self.statements_graph, aconst2)
            self._make_equal(abx, dn, dep=dep2)
            to_cache.append((aconst2, dep2))
            add += [dep2]

        return add, to_cache

    def _add_rconst(
        self, args: list[Point], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add new algebraic predicates of type eqratio-constant."""
        a, b, c, d, ratio = args

        num, den = ratio_to_num_den(ratio)
        nd, dn = self.symbols_graph.get_or_create_const_rat(num, den)

        if num == den:
            return self._add_cong([a, b, c, d], dep_body)

        ab = self.symbols_graph.get_or_create_segment(a, b, dep=None)
        cd = self.symbols_graph.get_or_create_segment(c, d, dep=None)

        self.symbols_graph.get_node_val(ab, dep=None)
        self.symbols_graph.get_node_val(cd, dep=None)

        if ab.val == cd.val:
            raise ValueError(f"{ab.name} and {cd.name} cannot be equal")

        args = [a, b, c, d, nd]
        i = 0
        for x, y, xy in [(a, b, ab), (c, d, cd)]:
            i += 1
            x_, y_ = list(xy._val._obj.points)
            if {x, y} == {x_, y_}:
                continue
            if (
                dep_body
                and IntrinsicRules.RCONST_FROM_CONG not in self.DISABLED_INTRINSIC_RULES
            ):
                rconst = Statement(Predicate.CONSTANT_RATIO, tuple(args))
                cong = Statement(Predicate.CONGRUENT, [x, y, x_, y_])
                dep_body = dep_body.extend(
                    self.statements_graph,
                    rconst,
                    cong,
                    extention_reason=Reason(IntrinsicRules.RCONST_FROM_CONG),
                )
            args[2 * i - 2] = x_
            args[2 * i - 1] = y_

        ab_cd, cd_ab, why = self.symbols_graph.get_or_create_ratio_from_segments(
            ab, cd, dep=None
        )

        rconst = Statement(Predicate.CONSTANT_RATIO, [a, b, c, d, nd])
        if IntrinsicRules.RCONST_FROM_RATIO not in self.DISABLED_INTRINSIC_RULES:
            dep_body = dep_body.extend_by_why(
                self.statements_graph,
                rconst,
                why=why,
                extention_reason=Reason(IntrinsicRules.RCONST_FROM_RATIO),
            )

        lab, lcd = ab_cd._l
        a, b = list(lab._obj.points)
        c, d = list(lcd._obj.points)

        add = []
        to_cache = []
        if not is_equal(ab_cd, nd):
            dep1 = dep_body.build(self.statements_graph, rconst)
            self._make_equal(nd, ab_cd, dep=dep1)
            to_cache.append((rconst, dep1))
            add.append(dep1)

        if not is_equal(cd_ab, dn):
            rconst2 = Statement(Predicate.CONSTANT_RATIO, [c, d, a, b, dn])
            dep2 = dep_body.build(self.statements_graph, rconst2)
            self._make_equal(dn, cd_ab, dep=dep2)
            to_cache.append((rconst2, dep2))
            add.append(dep2)

        return add, to_cache

    def _add_lconst(
        self, args: tuple[Point, Point, Length], dep_body: DependencyBody
    ) -> tuple[list[Dependency], list[ToCache]]:
        """Add new algebraic predicates of type eqratio-constant."""
        a, b, length = args

        ab = self.symbols_graph.get_or_create_segment(a, b, dep=None)
        l_ab = self.symbols_graph.get_node_val(ab, dep=None)

        lconst = Statement(Predicate.CONSTANT_LENGTH, args)

        lconst_dep = dep_body.build(self.statements_graph, lconst)
        self._make_equal(length, l_ab, dep=lconst_dep)

        add = [lconst_dep]
        to_cache = [(lconst, lconst_dep)]
        return add, to_cache
