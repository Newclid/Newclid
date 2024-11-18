from __future__ import annotations
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Optional, TypeVar


from newclid.statements.statement import Statement

from newclid.dependencies.dependency import Dependency, Reason
from newclid.geometry import (
    Angle,
    AngleValue,
    Circle,
    Direction,
    Line,
    Symbol,
    Point,
    Ratio,
    all_angles,
    all_ratios,
    bfs_backtrack,
    is_equal,
)
from newclid.predicates import Predicate


if TYPE_CHECKING:
    from newclid.dependencies.why_graph import WhyHyperGraph


def why_dependency(
    statements_graph: "WhyHyperGraph",
    statement: "Statement",
    use_cache: bool = True,
) -> tuple[Reason, list[Dependency]]:
    if use_cache:
        cached_me = statements_graph.dependency_cache.get(statement)
        if cached_me is not None:
            return cached_me.reason, cached_me.why

    predicate = Predicate(statement.name)
    reason = Reason(f"why_{predicate.value}_resolution")

    if predicate is Predicate.IND:
        return reason, []

    why_predicate = PREDICATE_TO_WHY[predicate]
    _reason, why = why_predicate(statements_graph, statement)
    if _reason is not None:
        reason = _reason
    return reason, why


def _why_equal(x: Symbol, y: Symbol) -> list[Dependency]:
    if x == y:
        return []
    if not x._val or not y._val:
        return None
    if x._val == y._val:
        return []
    return x._val.why_equal([y._val])


def _why_para(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    a, b, c, d = statement.args

    if {a, b} == {c, d}:
        return []

    ab = statements_graph.symbols_graph.get_line(a, b)
    cd = statements_graph.symbols_graph.get_line(c, d)
    if ab == cd:
        if {a, b} == {c, d}:
            return None, []

        coll = Statement(Predicate.COLLINEAR, list({a, b, c, d}))
        coll_dep = statements_graph.build_resolved_dependency(coll, use_cache=False)
        return None, [coll_dep]

    whypara = []
    for (x, y), xy in zip([(a, b), (c, d)], [ab, cd]):
        x_, y_ = xy.points
        if {x, y} == {x_, y_}:
            continue
        collx = Statement(Predicate.COLLINEAR_X, [x, y, x_, y_])
        collx_dep = statements_graph.build_resolved_dependency(collx, use_cache=False)
        whypara.append(collx_dep)

    return None, whypara + _why_equal(ab, cd)


def _why_midpoint(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    m, a, b = statement.args
    ma = statements_graph.symbols_graph.get_segment(m, a)
    mb = statements_graph.symbols_graph.get_segment(m, b)
    coll = Statement(Predicate.COLLINEAR, [m, a, b])
    coll_dep = statements_graph.build_resolved_dependency(coll, use_cache=False)
    return None, [coll_dep] + _why_equal(ma, mb)


def _why_perp(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    a, b, c, d = statement.args
    ab = statements_graph.symbols_graph.get_line(a, b)
    cd = statements_graph.symbols_graph.get_line(c, d)

    why_perp = []
    for (x, y), xy in zip([(a, b), (c, d)], [ab, cd]):
        if xy is None:
            raise ValueError(
                f"Line {x.name.capitalize()}{y.name.capitalize()} does not exist"
            )

        x_, y_ = xy.points

        if {x, y} == {x_, y_}:
            continue
        collx = Statement(Predicate.COLLINEAR_X, [x, y, x_, y_])
        why_perp.append(
            statements_graph.build_resolved_dependency(collx, use_cache=False)
        )

    why_eqangle = _why_eqangle_directions(
        statements_graph, ab._val, cd._val, cd._val, ab._val
    )
    a, b = ab.points
    c, d = cd.points

    perp_repr = Statement(statement.name, [a, b, c, d])
    if perp_repr.hash_tuple != statement.hash_tuple:
        perp_repr_dep = statements_graph.build_dependency_from_statement(
            perp_repr, why=why_eqangle, reason=Reason("_why_perp_repr")
        )
        why_eqangle = [perp_repr_dep]

    if why_eqangle:
        why_perp += why_eqangle
    return None, why_perp


def _why_cong(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    a, b, c, d = statement.args
    ab = statements_graph.symbols_graph.get_segment(a, b)
    cd = statements_graph.symbols_graph.get_segment(c, d)
    return None, _why_equal(ab, cd)


def _why_coll(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    _, why = _line_of_and_why(statement.args)
    return None, why


def _why_collx(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    if statements_graph.statements_checker.check_coll(statement.args):
        args = list(set(statement.args))
        coll = Statement(Predicate.COLLINEAR, args)
        cached_dep = statements_graph.dependency_cache.get(coll)
        if cached_dep is not None:
            return None, [cached_dep]
        _, why = _line_of_and_why(args)
        return None, why

    para = Statement(Predicate.PARALLEL, statement.args)
    return _why_para(statements_graph, para)


def _line_of_and_why(
    points: list[Point],
) -> tuple[Optional[Line], Optional[list[Dependency]]]:
    """Why points are collinear."""
    for l0 in _get_lines_thru_all(*points):
        for line in l0.equivs():
            if all([p in line.edge_graph for p in points]):
                x, y = line.points
                colls = list({x, y} | set(points))
                why = line.why_coll(colls)
                if why is not None:
                    return line, why

    return None, None


def _get_lines_thru_all(*points: Point) -> list[Line]:
    line2count = defaultdict(lambda: 0)
    points = set(points)
    for p in points:
        for line_neighbor in p.neighbors(Line):
            line2count[line_neighbor] += 1
    return [line for line, count in line2count.items() if count == len(points)]


def _why_cyclic(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    _, why = _circle_of_and_why(statement.args)
    return None, why


def _circle_of_and_why(
    points: list[Point],
) -> tuple[Optional[Circle], Optional[list[Dependency]]]:
    """Why points are concyclic."""
    for initial_circle in _get_circles_thru_all(*points):
        for circle in initial_circle.equivs():
            if all([p in circle.edge_graph for p in points]):
                cycls = list(set(points))
                why = circle.why_cyclic(cycls)
                if why is not None:
                    return circle, why

    return None, None


def _get_circles_thru_all(*points: Point) -> list[Circle]:
    circle2count = defaultdict(lambda: 0)
    points = set(points)
    for point in points:
        for circle in point.neighbors(Circle):
            circle2count[circle] += 1
    return [c for c, count in circle2count.items() if count == len(points)]


def _why_circle(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    o, a, b, c = statement.args
    oa = statements_graph.symbols_graph.get_segment(o, a)
    ob = statements_graph.symbols_graph.get_segment(o, b)
    oc = statements_graph.symbols_graph.get_segment(o, c)
    return None, _why_equal(oa, ob) + _why_equal(oa, oc)


def _why_eqangle(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    a, b, c, d, m, n, p, q = statement.args

    ab, why1 = statements_graph.symbols_graph.get_line_thru_pair_why(a, b)
    cd, why2 = statements_graph.symbols_graph.get_line_thru_pair_why(c, d)
    mn, why3 = statements_graph.symbols_graph.get_line_thru_pair_why(m, n)
    pq, why4 = statements_graph.symbols_graph.get_line_thru_pair_why(p, q)

    if ab is None or cd is None or mn is None or pq is None:
        para_points = None
        if {a, b} == {m, n}:
            para_points = [c, d, p, q]
        elif {a, b} == {c, d}:
            para_points = [p, q, m, n]
        elif {c, d} == {p, q}:
            para_points = [a, b, m, n]
        elif {p, q} == {m, n}:
            para_points = [a, b, c, d]
        para = Statement(Predicate.PARALLEL, para_points)
        para_dep = statements_graph.build_resolved_dependency(para, use_cache=False)
        return None, [para_dep]

    why_eqangle = []
    for (x, y), xy, whyxy in zip(
        [(a, b), (c, d), (m, n), (p, q)],
        [ab, cd, mn, pq],
        [why1, why2, why3, why4],
    ):
        x_, y_ = xy.points
        if {x, y} == {x_, y_}:
            continue
        collx = Statement(Predicate.COLLINEAR_X, [x, y, x_, y_])
        collx_dep = statements_graph.build_dependency_from_statement(
            collx, why=whyxy, reason=Reason("_why_eqangle_collx")
        )
        why_eqangle.append(collx_dep)

    a, b = ab.points
    c, d = cd.points
    m, n = mn.points
    p, q = pq.points

    representent_statement = Statement(statement.name, [a, b, c, d, m, n, p, q])
    different_from_repr = representent_statement.hash_tuple != statement.hash_tuple

    why_eqangle_values = None
    if ab._val and cd._val and mn._val and pq._val:
        why_eqangle_values = _why_eqangle_directions(
            statements_graph, ab._val, cd._val, mn._val, pq._val
        )

    if why_eqangle_values:
        if different_from_repr:
            eqangle = Statement(Predicate.EQANGLE, [a, b, c, d, m, n, p, q])
            eqangle_dep = statements_graph.build_dependency_from_statement(
                eqangle, why=why_eqangle_values, reason=Reason("_why_eqangle_eqangle")
            )
            why_eqangle_values = [eqangle_dep]
        return None, why_eqangle + why_eqangle_values

    if (ab == cd and mn == pq) or (ab == mn and cd == pq):
        return None, why_eqangle

    equal_pair_points, equal_pair_lines = _find_equal_pair(
        a, b, c, d, m, n, p, q, ab, cd, mn, pq
    )
    if equal_pair_points is not None and equal_pair_lines is not None:
        why_eqangle += _maybe_make_equal_pairs(
            statements_graph, *equal_pair_points, *equal_pair_lines
        )
        return None, why_eqangle

    if is_equal(ab, mn) or is_equal(cd, pq):
        para1 = Statement(Predicate.PARALLEL, [a, b, m, n])
        dep1 = statements_graph.build_resolved_dependency(para1, use_cache=False)
        para2 = Statement(Predicate.PARALLEL, [c, d, p, q])
        dep2 = statements_graph.build_resolved_dependency(para2, use_cache=False)
        why_eqangle += [dep1, dep2]

    elif is_equal(ab, cd) or is_equal(mn, pq):
        para1 = Statement(Predicate.PARALLEL, [a, b, c, d])
        dep1 = statements_graph.build_resolved_dependency(para1, use_cache=False)
        para2 = Statement(Predicate.PARALLEL, [m, n, p, q])
        dep2 = statements_graph.build_resolved_dependency(para2, use_cache=False)
        why_eqangle += [dep1, dep2]
    elif ab._val and cd._val and mn._val and pq._val:
        why_eqangle = _why_eqangle_directions(
            statements_graph, ab._val, cd._val, mn._val, pq._val
        )

    return None, why_eqangle


def _why_eqratio(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    a, b, c, d, m, n, p, q = statement.args
    ab = statements_graph.symbols_graph.get_segment(a, b)
    cd = statements_graph.symbols_graph.get_segment(c, d)
    mn = statements_graph.symbols_graph.get_segment(m, n)
    pq = statements_graph.symbols_graph.get_segment(p, q)

    why_eqratio = []
    if ab is None or cd is None or mn is None or pq is None:
        congruent_points = None
        if {a, b} == {m, n}:
            congruent_points = [c, d, p, q]
        elif {a, b} == {c, d}:
            congruent_points = [p, q, m, n]
        elif {c, d} == {p, q}:
            congruent_points = [a, b, m, n]
        elif {p, q} == {m, n}:
            congruent_points = [a, b, c, d]

        if congruent_points is not None:
            cong = Statement(Predicate.CONGRUENT, congruent_points)
            cong_dep = statements_graph.build_resolved_dependency(cong, use_cache=False)
            why_eqratio = [cong_dep]
        return None, why_eqratio

    if ab._val and cd._val and mn._val and pq._val:
        why_eqratio_from_directions = _why_eqratio_directions(
            statements_graph, ab._val, cd._val, mn._val, pq._val
        )
        if why_eqratio_from_directions:
            why_eqratio += why_eqratio_from_directions

    if (ab == cd and mn == pq) or (ab == mn and cd == pq):
        return None, []

    equal_pair_points, equal_pair_lines = _find_equal_pair(
        a, b, c, d, m, n, p, q, ab, cd, mn, pq
    )
    if equal_pair_points is not None:
        why_eqratio += _maybe_make_equal_pairs(
            statements_graph, *equal_pair_points, *equal_pair_lines
        )
        return None, why_eqratio

    if is_equal(ab, mn) or is_equal(cd, pq):
        cong1 = Statement(Predicate.CONGRUENT, [a, b, m, n])
        dep1 = statements_graph.build_resolved_dependency(cong1, use_cache=False)
        cong2 = Statement(Predicate.CONGRUENT, [c, d, p, q])
        dep2 = statements_graph.build_resolved_dependency(cong2, use_cache=False)
        why_eqratio += [dep1, dep2]
    elif is_equal(ab, cd) or is_equal(mn, pq):
        cong1 = Statement(Predicate.CONGRUENT, [a, b, c, d])
        dep1 = statements_graph.build_resolved_dependency(cong1, use_cache=False)
        cong2 = Statement(Predicate.CONGRUENT, [m, n, p, q])
        dep2 = statements_graph.build_resolved_dependency(cong2, use_cache=False)
        why_eqratio += [dep1, dep2]
    elif ab._val and cd._val and mn._val and pq._val:
        why_eqratio = _why_eqratio_directions(
            statements_graph, ab._val, cd._val, mn._val, pq._val
        )

    return None, why_eqratio


def _why_aconst(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    a, b, c, d, ang0 = statement.args

    measure: AngleValue = ang0._val
    for ang in measure.neighbors(Angle):
        if ang == ang0:
            continue
        d1, d2 = ang._d
        l1, l2 = d1._obj, d2._obj
        (a1, b1), (c1, d1) = l1.points, l2.points

        if not statements_graph.statements_checker.check_para_or_coll(
            [a, b, a1, b1]
        ) or not statements_graph.statements_checker.check_para_or_coll([c, d, c1, d1]):
            continue

        why_aconst = []
        for args in [(a, b, a1, b1), (c, d, c1, d1)]:
            if statements_graph.statements_checker.check_coll(args):
                if len(set(args)) <= 2:
                    continue
                coll = Statement(Predicate.COLLINEAR, args)
                coll_dep = statements_graph.build_resolved_dependency(
                    coll, use_cache=False
                )
                why_aconst.append(coll_dep)
            else:
                para = Statement(Predicate.PARALLEL, args)
                para_dep = statements_graph.build_resolved_dependency(
                    para, use_cache=False
                )
                why_aconst.append(para_dep)

        why_aconst += _why_equal(ang, ang0)
        return None, why_aconst


def _why_rconst(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    a, b, c, d, rat0 = statement.args

    val: AngleValue = rat0._val
    for rat in val.neighbors(Ratio):
        if rat == rat0:
            continue
        l1, l2 = rat._l
        s1, s2 = l1._obj, l2._obj
        (a1, b1), (c1, d1) = list(s1.points), list(s2.points)

        if not statements_graph.statements_checker.check_cong(
            [a, b, a1, b1]
        ) or not statements_graph.statements_checker.check_cong([c, d, c1, d1]):
            continue

        why_rconst = []
        for args in [(a, b, a1, b1), (c, d, c1, d1)]:
            if len(set(args)) > 2:
                cong = Statement(Predicate.CONGRUENT, args)
                why_rconst.append(
                    statements_graph.build_resolved_dependency(cong, use_cache=False)
                )

        why_rconst += _why_equal(rat, rat0)
        return None, why_rconst


def _why_numerical(
    statements_graph: "WhyHyperGraph", statement: "Statement"
) -> tuple[Optional[Reason], list[Dependency]]:
    return None, []


PREDICATE_TO_WHY: dict[
    Predicate,
    Callable[
        ["WhyHyperGraph", "Statement", int],
        tuple[Optional[Reason], list[Dependency]],
    ],
] = {
    Predicate.PARALLEL: _why_para,
    Predicate.MIDPOINT: _why_midpoint,
    Predicate.PERPENDICULAR: _why_perp,
    Predicate.CONGRUENT: _why_cong,
    Predicate.COLLINEAR: _why_coll,
    Predicate.COLLINEAR_X: _why_collx,
    Predicate.CYCLIC: _why_cyclic,
    Predicate.CIRCLE: _why_circle,
    Predicate.EQANGLE: _why_eqangle,
    Predicate.EQANGLE6: _why_eqangle,
    Predicate.EQRATIO: _why_eqratio,
    Predicate.EQRATIO6: _why_eqratio,
    Predicate.CONSTANT_ANGLE: _why_aconst,
    Predicate.CONSTANT_RATIO: _why_rconst,
    Predicate.DIFFERENT: _why_numerical,
    Predicate.NON_PARALLEL: _why_numerical,
    Predicate.NON_PERPENDICULAR: _why_numerical,
    Predicate.NON_COLLINEAR: _why_numerical,
    Predicate.SAMESIDE: _why_numerical,
}


P = TypeVar("P")
L = TypeVar("L")


def _find_equal_pair(
    a: P, b: P, c: P, d: P, m: P, n: P, p: P, q: P, ab: L, cd: L, mn: L, pq: L
) -> tuple[Optional[list[P]], Optional[list[L]]]:
    points = None
    lines = None
    if ab == mn:
        points = [a, b, c, d, m, n, p, q]
        lines = [ab, mn]
    elif cd == pq:
        points = [c, d, a, b, p, q, m, n]
        lines = [cd, pq]
    elif ab == cd:
        points = [a, b, m, n, c, d, p, q]
        lines = [ab, cd]
    elif mn == pq:
        points = [m, n, a, b, p, q, c, d]
        lines = [mn, pq]

    return points, lines


def _maybe_make_equal_pairs(
    statements_graph: "WhyHyperGraph",
    a: Point,
    b: Point,
    c: Point,
    d: Point,
    m: Point,
    n: Point,
    p: Point,
    q: Point,
    ab: Line,
    mn: Line,
) -> list["Dependency"]:
    """Make a-b:c-d==m-n:p-q in case a-b==m-n or c-d==p-q."""
    if ab != mn:
        return
    why = []
    eqpredicate = Predicate.PARALLEL if isinstance(ab, Line) else Predicate.CONGRUENT
    colls = [a, b, m, n]
    if len(set(colls)) > 2 and eqpredicate is Predicate.PARALLEL:
        collx = Statement(Predicate.COLLINEAR_X, colls)
        why.append(statements_graph.build_resolved_dependency(collx, use_cache=False))

    eq_statement = Statement(eqpredicate, [c, d, p, q])
    why.append(
        statements_graph.build_resolved_dependency(eq_statement, use_cache=False)
    )
    return why


def _why_eqangle_directions(
    statements_graph: "WhyHyperGraph",
    d1: Direction,
    d2: Direction,
    d3: Direction,
    d4: Direction,
) -> Optional[list[Dependency]]:
    """Why two angles are equal, returns a Dependency objects."""
    all12 = list(all_angles(d1, d2))
    all34 = list(all_angles(d3, d4))

    min_why = None
    for ang12, d1s, d2s in all12:
        for ang34, d3s, d4s in all34:
            why0 = _why_equal(ang12, ang34)
            if why0 is None:
                continue
            d1_, d2_ = ang12._d
            d3_, d4_ = ang34._d
            why1 = bfs_backtrack(d1, [d1_], d1s)
            why2 = bfs_backtrack(d2, [d2_], d2s)
            why3 = bfs_backtrack(d3, [d3_], d3s)
            why4 = bfs_backtrack(d4, [d4_], d4s)
            why = why0 + why1 + why2 + why3 + why4
            if min_why is None or len(why) < len(min_why[0]):
                min_why = why, ang12, ang34, why0, why1, why2, why3, why4

    if min_why is None:
        return None

    _, ang12, ang34, why0, why1, why2, why3, why4 = min_why
    why0 = _why_equal(ang12, ang34)
    d1_, d2_ = ang12._d
    d3_, d4_ = ang34._d

    if d1 == d1_ and d2 == d2_ and d3 == d3_ and d4 == d4_:
        return why0

    (a_, b_), (c_, d_) = d1_._obj.points, d2_._obj.points
    (e_, f_), (g_, h_) = d3_._obj.points, d4_._obj.points
    deps = []
    if why0:
        eqangle = Statement(Predicate.EQANGLE, [a_, b_, c_, d_, e_, f_, g_, h_])
        deps.append(
            statements_graph.build_dependency_from_statement(
                eqangle, why=why0, reason=Reason("")
            )
        )

    (a, b), (c, d) = d1._obj.points, d2._obj.points
    (e, f), (g, h) = d3._obj.points, d4._obj.points
    for why, d_xy, (x, y), d_xy_, (x_, y_) in zip(
        [why1, why2, why3, why4],
        [d1, d2, d3, d4],
        [(a, b), (c, d), (e, f), (g, h)],
        [d1_, d2_, d3_, d4_],
        [(a_, b_), (c_, d_), (e_, f_), (g_, h_)],
    ):
        xy, xy_ = d_xy._obj, d_xy_._obj
        if why:
            if xy == xy_:
                predicate = Predicate.COLLINEAR_X
            else:
                predicate = Predicate.PARALLEL
            because_statement = Statement(predicate, [x_, y_, x, y])
            deps.append(
                statements_graph.build_dependency_from_statement(
                    because_statement, why=why, reason=Reason("")
                )
            )

    return deps


def _why_eqratio_directions(
    statements_graph: "WhyHyperGraph",
    d1: Direction,
    d2: Direction,
    d3: Direction,
    d4: Direction,
) -> Optional[list[Dependency]]:
    """Why two ratios are equal, returns a Dependency objects."""
    all12 = list(all_ratios(d1, d2))
    all34 = list(all_ratios(d3, d4))

    if not all12 or not all34:
        return None

    min_why = None
    for ang12, d1s, d2s in all12:
        for ang34, d3s, d4s in all34:
            why0 = _why_equal(ang12, ang34)
            if why0 is None:
                continue
            d1_, d2_ = ang12._l
            d3_, d4_ = ang34._l
            why1 = bfs_backtrack(d1, [d1_], d1s)
            why2 = bfs_backtrack(d2, [d2_], d2s)
            why3 = bfs_backtrack(d3, [d3_], d3s)
            why4 = bfs_backtrack(d4, [d4_], d4s)
            why = why0 + why1 + why2 + why3 + why4
            if min_why is None or len(why) < len(min_why[0]):
                min_why = why, ang12, ang34, why0, why1, why2, why3, why4

    _, ang12, ang34, why0, why1, why2, why3, why4 = min_why
    d1_, d2_ = ang12._l
    d3_, d4_ = ang34._l

    if d1 == d1_ and d2 == d2_ and d3 == d3_ and d4 == d4_:
        return why0

    (a_, b_), (c_, d_) = d1_._obj.points, d2_._obj.points
    (e_, f_), (g_, h_) = d3_._obj.points, d4_._obj.points
    deps = []
    if why0:
        eqratio = Statement(Predicate.EQRATIO, [a_, b_, c_, d_, e_, f_, g_, h_])
        deps.append(
            statements_graph.build_dependency_from_statement(
                eqratio, why=why0, reason=Reason("")
            )
        )

    (a, b), (c, d) = d1._obj.points, d2._obj.points
    (e, f), (g, h) = d3._obj.points, d4._obj.points
    for why, (x, y), (x_, y_) in zip(
        [why1, why2, why3, why4],
        [(a, b), (c, d), (e, f), (g, h)],
        [(a_, b_), (c_, d_), (e_, f_), (g_, h_)],
    ):
        if not why:
            continue
        cong = Statement(Predicate.CONGRUENT, [x, y, x_, y_])
        deps.append(
            statements_graph.build_dependency_from_statement(
                cong, why=why, reason=Reason("")
            )
        )

    return deps
