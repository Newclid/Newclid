"""Implements theorem matching functions for the Deductive Database (DD)."""

from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Generator, Optional

import newclid.combinatorics as comb

from newclid.defs.clause import Construction
from newclid.predicates import Predicate
from newclid.agent.agents_interface import Mapping
from newclid.points_manipulation import (
    diff_point,
    intersect1,
    rotate_contri,
    rotate_simtri,
)
from newclid.geometry import (
    Angle,
    Circle,
    Direction,
    Length,
    Line,
    AngleValue,
    Point,
    Ratio,
    Segment,
    RatioValue,
    is_equal,
)
from newclid.numerical.check import check_ncoll_numerical, same_clock


if TYPE_CHECKING:
    from newclid.proof import Proof
    from newclid.defs.clause import Clause
    from newclid.theorem import Theorem


def match_eqratio_eqratio_eqratio(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqratio a b c d m n p q, eqratio c d e f p q r u => eqratio a b e f m n r u."""
    for m1 in proof.symbols_graph.type2nodes[RatioValue]:
        for m2 in proof.symbols_graph.type2nodes[RatioValue]:
            rats1 = []
            for rat in m1.neighbors(Ratio):
                l1, l2 = rat.lengths
                if l1 is None or l2 is None:
                    continue
                rats1.append((l1, l2))

            rats2 = []
            for rat in m2.neighbors(Ratio):
                l1, l2 = rat.lengths
                if l1 is None or l2 is None:
                    continue
                rats2.append((l1, l2))

            pairs = []
            for (l1, l2), (l3, l4) in comb.cross_product(rats1, rats2):
                if l2 == l3:
                    pairs.append((l1, l2, l4))

            for (l1, l12, l2), (l3, l34, l4) in comb.arrangement_pairs(pairs):
                if (l1, l12, l2) == (l3, l34, l4):
                    continue
                if l1 == l2 or l3 == l4:
                    continue
                if l1 == l12 or l12 == l2 or l3 == l34 or l4 == l34:
                    continue
                # d12 - d1 = d34 - d3 = m1
                # d2 - d12 = d4 - d34 = m2
                # => d2 - d1 = d4 - d3 (= m1+m2)
                a, b = proof.symbols_graph.two_points_of_length(l1)
                c, d = proof.symbols_graph.two_points_of_length(l12)
                m, n = proof.symbols_graph.two_points_of_length(l3)
                p, q = proof.symbols_graph.two_points_of_length(l34)
                # eqangle a b c d m n p q
                e, f = proof.symbols_graph.two_points_of_length(l2)
                r, u = proof.symbols_graph.two_points_of_length(l4)
                yield dict(zip("abcdefmnpqru", [a, b, c, d, e, f, m, n, p, q, r, u]))


def match_eqangle_eqangle_eqangle(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle a b c d m n p q, eqangle c d e f p q r u => eqangle a b e f m n r u."""
    for m1 in proof.symbols_graph.type2nodes[AngleValue]:
        for m2 in proof.symbols_graph.type2nodes[AngleValue]:
            angs1 = []
            for ang in m1.neighbors(Angle):
                d1, d2 = ang.directions
                if d1 is None or d2 is None:
                    continue
                angs1.append((d1, d2))

            angs2 = []
            for ang in m2.neighbors(Angle):
                d1, d2 = ang.directions
                if d1 is None or d2 is None:
                    continue
                angs2.append((d1, d2))

            pairs = []
            for (d1, d2), (d3, d4) in comb.cross_product(angs1, angs2):
                if d2 == d3:
                    pairs.append((d1, d2, d4))

            for (d1, d12, d2), (d3, d34, d4) in comb.arrangement_pairs(pairs):
                if (d1, d12, d2) == (d3, d34, d4):
                    continue
                if d1 == d2 or d3 == d4:
                    continue
                if d1 == d12 or d12 == d2 or d3 == d34 or d4 == d34:
                    continue
                # d12 - d1 = d34 - d3 = m1
                # d2 - d12 = d4 - d34 = m2
                # => d2 - d1 = d4 - d3
                a, b = proof.symbols_graph.two_points_on_direction(d1)
                c, d = proof.symbols_graph.two_points_on_direction(d12)
                m, n = proof.symbols_graph.two_points_on_direction(d3)
                p, q = proof.symbols_graph.two_points_on_direction(d34)
                # eqangle a b c d m n p q
                e, f = proof.symbols_graph.two_points_on_direction(d2)
                r, u = proof.symbols_graph.two_points_on_direction(d4)
                yield dict(zip("abcdefmnpqru", [a, b, c, d, e, f, m, n, p, q, r, u]))


def match_perp_perp_npara_eqangle(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match perp A B C D, perp E F G H, npara A B E F => eqangle A B E F C D G H."""
    dpairs = []
    for ang in proof.symbols_graph.vhalfpi.neighbors(Angle):
        d1, d2 = ang.directions
        if d1 is None or d2 is None:
            continue
        dpairs.append((d1, d2))

    for (d1, d2), (d3, d4) in comb.arrangement_pairs(dpairs):
        a, b = proof.symbols_graph.two_points_on_direction(d1)
        c, d = proof.symbols_graph.two_points_on_direction(d2)
        m, n = proof.symbols_graph.two_points_on_direction(d3)
        p, q = proof.symbols_graph.two_points_on_direction(d4)
        if proof.statements.checker.check_npara([a, b, m, n]):
            if ({a, b}, {c, d}) == ({m, n}, {p, q}):
                continue
            if ({a, b}, {c, d}) == ({p, q}, {m, n}):
                continue

            yield dict(zip("ABCDEFGH", [a, b, c, d, m, n, p, q]))


def match_circle_coll_eqangle_midp(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match circle O A B C, coll M B C, eqangle A B A C O B O M => midp M B C."""
    for p, a, b, c in proof.statements.enumerator.all(Predicate.CIRCLE):
        ab = proof.symbols_graph.get_line(a, b)
        if ab is None:
            continue
        if ab.val is None:
            continue
        ac = proof.symbols_graph.get_line(a, c)
        if ac is None:
            continue
        if ac.val is None:
            continue
        pb = proof.symbols_graph.get_line(p, b)
        if pb is None:
            continue
        if pb.val is None:
            continue

        bc = proof.symbols_graph.get_line(b, c)
        if bc is None:
            continue
        bc_points = bc.neighbors(Point, return_set=True)

        anga, _ = proof.symbols_graph.get_angle(ab.val, ac.val)

        for angp in pb.val.neighbors(Angle):
            if not is_equal(anga, angp):
                continue

            _, d = angp.directions
            for line_neighbor in d.neighbors(Line):
                l_points = line_neighbor.neighbors(Point, return_set=True)
                m = intersect1(bc_points, l_points)
                if m is not None:
                    yield dict(zip("ABCMO", [a, b, c, m, p]))


def match_midp_perp_cong(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match midp M A B, perp O M A B => cong O A O B."""
    for m, a, b in proof.statements.enumerator._all_midps():
        ab = proof.symbols_graph.get_line(a, b)
        for line_neighbor in m.neighbors(Line):
            if proof.statements.checker.check_perpl(line_neighbor, ab):
                for o in line_neighbor.neighbors(Point):
                    if o != m:
                        yield dict(zip("ABMO", [a, b, m, o]))


def match_cyclic_eqangle_cong(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match cyclic A B C P Q R, eqangle C A C B R P R Q => cong A B P Q."""
    for c in proof.symbols_graph.type2nodes[Circle]:
        ps = c.neighbors(Point)
        for (a, b, c), (x, y, z) in comb.arrangement_pairs(
            list(comb.permutations_triplets(ps))
        ):
            if {a, b, c} == {x, y, z}:
                continue
            if proof.statements.checker.check_eqangle([c, a, c, b, z, x, z, y]):
                yield dict(zip("ABCPQR", [a, b, c, x, y, z]))


def match_circle_eqangle_perp(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match circle O A B C, eqangle A X A B C A C B => perp O A A X."""
    for p, a, b, c in proof.statements.enumerator.all(Predicate.CIRCLE):
        ca = proof.symbols_graph.get_line(c, a)
        if ca is None:
            continue
        cb = proof.symbols_graph.get_line(c, b)
        if cb is None:
            continue
        ab = proof.symbols_graph.get_line(a, b)
        if ab is None:
            continue

        if ca.val is None:
            continue
        if cb.val is None:
            continue
        if ab.val is None:
            continue

        c_ang, _ = proof.symbols_graph.get_angle(cb.val, ca.val)
        if c_ang is None:
            continue

        for ang in ab.val.neighbors(Angle):
            if is_equal(ang, c_ang):
                _, d = ang.directions
                for line_neighbor in d.neighbors(Line):
                    if a not in line_neighbor.neighbors(Point):
                        continue
                    x = diff_point(line_neighbor, a)
                    if x is None:
                        continue
                    yield dict(zip("OABCX", [p, a, b, c, x]))
                break


def match_circle_perp_eqangle(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match circle O A B C, perp O A A X => eqangle A X A B C A C B."""
    for p, a, b, c in proof.statements.enumerator.all(Predicate.CIRCLE):
        pa = proof.symbols_graph.get_line(p, a)
        if pa is None:
            continue
        if pa.val is None:
            continue
        for line_neighbor in a.neighbors(Line):
            if proof.statements.checker.check_perpl(pa, line_neighbor):
                x = diff_point(line_neighbor, a)
                if x is not None:
                    yield dict(zip("OABCX", [p, a, b, c, x]))


def match_perp_perp_ncoll_para(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match perp A B C D, perp C D E F, ncoll A B E => para A B E F."""
    d2d = defaultdict(list)
    for ang in proof.symbols_graph.vhalfpi.neighbors(Angle):
        d1, d2 = ang.directions
        if d1 is None or d2 is None:
            continue
        d2d[d1] += [d2]
        d2d[d2] += [d1]

    for x, ys in d2d.items():
        if len(ys) < 2:
            continue
        c, d = proof.symbols_graph.two_points_on_direction(x)
        for y1, y2 in comb.arrangement_pairs(ys):
            a, b = proof.symbols_graph.two_points_on_direction(y1)
            e, f = proof.symbols_graph.two_points_on_direction(y2)
            if check_ncoll_numerical([a.num, b.num, e.num]):
                yield dict(zip("ABCDEF", [a, b, c, d, e, f]))


def match_eqangle6_ncoll_cong(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle6 A O A B B A B O, ncoll O A B => cong O A O B."""
    for a in proof.symbols_graph.type2nodes[Point]:
        for b, c in comb.arrangement_pairs(proof.symbols_graph.type2nodes[Point]):
            if a == b or a == c:
                continue
            if proof.statements.checker.check_eqangle([b, a, b, c, c, b, c, a]):
                if proof.statements.checker.check_ncoll([a, b, c]):
                    yield dict(zip("OAB", [a, b, c]))


def match_eqangle_perp_perp(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle A B P Q C D U V, perp P Q U V => perp A B C D."""
    for ang in proof.symbols_graph.vhalfpi.neighbors(Angle):
        # d1 perp d2
        d1, d2 = ang.directions
        if d1 is None or d2 is None:
            continue
        for d3, d4 in comb.arrangement_pairs(proof.symbols_graph.type2nodes[Direction]):
            if d1 == d3 or d2 == d4:
                continue
            # if d1 - d3 = d2 - d4 => d3 perp d4
            a13, a31 = proof.symbols_graph.get_angle(d1, d3)
            a24, a42 = proof.symbols_graph.get_angle(d2, d4)
            if a13 is None or a31 is None or a24 is None or a42 is None:
                continue
            if is_equal(a13, a24) and is_equal(a31, a42):
                a, b = proof.symbols_graph.two_points_on_direction(d1)
                c, d = proof.symbols_graph.two_points_on_direction(d2)
                m, n = proof.symbols_graph.two_points_on_direction(d3)
                p, q = proof.symbols_graph.two_points_on_direction(d4)
                yield dict(zip("ABCDPQUV", [m, n, p, q, a, b, c, d]))


def match_eqangle_ncoll_cyclic(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle6 P A P B Q A Q B, ncoll P Q A B => cyclic A B P Q."""
    linepairs = proof.statements.enumerator.all_eqangles_distinct_linepairss()
    for l1, l2, l3, l4 in linepairs:
        if len(set([l1, l2, l3, l4])) < 4:
            continue  # they all must be distinct.

        p1s = l1.neighbors(Point, return_set=True)
        p2s = l2.neighbors(Point, return_set=True)
        p3s = l3.neighbors(Point, return_set=True)
        p4s = l4.neighbors(Point, return_set=True)

        p = intersect1(p1s, p2s)
        if not p:
            continue
        q = intersect1(p3s, p4s)
        if not q:
            continue
        a = intersect1(p1s, p3s)
        if not a:
            continue
        b = intersect1(p2s, p4s)
        if not b:
            continue
        if len(set([a, b, p, q])) < 4:
            continue

        if not proof.statements.checker.check_ncoll([a, b, p, q]):
            continue

        yield dict(zip("ABPQ", [a, b, p, q]))


def match_eqangle_para(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle A B P Q C D P Q => para A B C D."""
    for measure in proof.symbols_graph.type2nodes[AngleValue]:
        angs = measure.neighbors(Angle)
        d12, d21 = defaultdict(list), defaultdict(list)
        for ang in angs:
            d1, d2 = ang.directions
            if d1 is None or d2 is None:
                continue
            d12[d1].append(d2)
            d21[d2].append(d1)

        for d1, d2s in d12.items():
            a, b = proof.symbols_graph.two_points_on_direction(d1)
            for d2, d3 in comb.arrangement_pairs(d2s):
                c, d = proof.symbols_graph.two_points_on_direction(d2)
                e, f = proof.symbols_graph.two_points_on_direction(d3)
                yield dict(zip("ABCDPQ", [c, d, e, f, a, b]))


def match_cyclic_eqangle(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match cyclic A B P Q => eqangle P A P B Q A Q B."""
    record = set()
    for a, b, c, d in g_matcher(Predicate.CYCLIC.value):
        if (a, b, c, d) in record:
            continue
        record.add((a, b, c, d))
        record.add((a, b, d, c))
        record.add((b, a, c, d))
        record.add((b, a, d, c))
        yield dict(zip("ABPQ", [a, b, c, d]))


def match_cong_cong_cong_cyclic(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match cong O A O B, cong O B O C, cong O C O D => cyclic A B C D."""
    for lenght in proof.symbols_graph.type2nodes[Length]:
        p2p = defaultdict(list)
        for s in lenght.neighbors(Segment):
            a, b = s.points
            p2p[a].append(b)
            p2p[b].append(a)

        for p, ps in p2p.items():
            if len(ps) >= 4:
                for a, b, c, d in comb.arrangement_quadruplets(ps):
                    yield dict(zip("OABCD", [p, a, b, c, d]))


def match_cong_cong_cong_ncoll_contri(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match cong A B P Q, cong B C Q R, cong C A R P, ncoll A B C => contri* A B C P Q R."""
    record = set()
    for a, b, p, q in g_matcher(Predicate.CONGRUENT.value):
        for c in proof.symbols_graph.type2nodes[Point]:
            for r in proof.symbols_graph.type2nodes[Point]:
                if any([x in record for x in rotate_simtri(a, b, c, p, q, r)]):
                    continue
                if not proof.statements.checker.check_ncoll([a, b, c]):
                    continue
                if proof.statements.checker.check_cong(
                    [b, c, q, r]
                ) and proof.statements.checker.check_cong([c, a, r, p]):
                    record.add((a, b, c, p, q, r))
                    yield dict(zip("ABCPQR", [a, b, c, p, q, r]))


def match_cong_cong_eqangle6_ncoll_contri(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match cong A B P Q, cong B C Q R, eqangle6 B A B C Q P Q R, ncoll A B C => contri* A B C P Q R."""
    record = set()
    for a, b, p, q in g_matcher(Predicate.CONGRUENT.value):
        for c in proof.symbols_graph.type2nodes[Point]:
            if c in (a, b):
                continue
            for r in proof.symbols_graph.type2nodes[Point]:
                if r in (p, q):
                    continue

                in_record = False
                for x in [
                    (c, b, a, r, q, p),
                    (p, q, r, a, b, c),
                    (r, q, p, c, b, a),
                ]:
                    if x in record:
                        in_record = True
                        break

                if in_record:
                    continue

                if not proof.statements.checker.check_cong([b, c, q, r]):
                    continue
                if not proof.statements.checker.check_ncoll([a, b, c]):
                    continue

                if same_clock(a.num, b.num, c.num, p.num, q.num, r.num):
                    if proof.statements.checker.check_eqangle([b, a, b, c, q, p, q, r]):
                        record.add((a, b, c, p, q, r))
                        yield dict(zip("ABCPQR", [a, b, c, p, q, r]))
                else:
                    if proof.statements.checker.check_eqangle([b, a, b, c, q, r, q, p]):
                        record.add((a, b, c, p, q, r))
                        yield dict(zip("ABCPQR", [a, b, c, p, q, r]))


def match_eqratio6_eqangle6_ncoll_simtri(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqratio6 B A B C Q P Q R, eqratio6 C A C B R P R Q, ncoll A B C => simtri* A B C P Q R."""
    enums = g_matcher(Predicate.EQRATIO6.value)

    record = set()
    for b, a, b, c, q, p, q, r in enums:
        if (a, b, c) == (p, q, r):
            continue
        if any([x in record for x in rotate_simtri(a, b, c, p, q, r)]):
            continue
        if not proof.statements.checker.check_ncoll([a, b, c]):
            continue

        if same_clock(a.num, b.num, c.num, p.num, q.num, r.num):
            if proof.statements.checker.check_eqangle([b, a, b, c, q, p, q, r]):
                record.add((a, b, c, p, q, r))
                yield dict(zip("ABCPQR", [a, b, c, p, q, r]))
        elif proof.statements.checker.check_eqangle([b, a, b, c, q, r, q, p]):
            record.add((a, b, c, p, q, r))
            yield dict(zip("ABCPQR", [a, b, c, p, q, r]))


def match_eqangle6_eqangle6_ncoll_simtri(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle6 B A B C Q P Q R, eqangle6 C A C B R P R Q, ncoll A B C => simtri A B C P Q R."""
    enums = g_matcher(Predicate.EQANGLE6.value)

    record = set()
    for b, a, b, c, q, p, q, r in enums:
        if (a, b, c) == (p, q, r):
            continue
        if any([x in record for x in rotate_simtri(a, b, c, p, q, r)]):
            continue
        if not proof.statements.checker.check_eqangle([c, a, c, b, r, p, r, q]):
            continue
        if not proof.statements.checker.check_ncoll([a, b, c]):
            continue

        mapping = dict(zip("ABCPQR", [a, b, c, p, q, r]))
        record.add((a, b, c, p, q, r))
        yield mapping


def match_eqratio6_eqratio6_ncoll_simtri(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqratio6 B A B C Q P Q R, eqratio6 C A C B R P R Q, ncoll A B C => simtri* A B C P Q R."""
    enums = g_matcher(Predicate.EQRATIO6.value)

    record = set()
    for b, a, b, c, q, p, q, r in enums:
        if (a, b, c) == (p, q, r):
            continue
        if any([x in record for x in rotate_simtri(a, b, c, p, q, r)]):
            continue
        if not proof.statements.checker.check_eqratio([c, a, c, b, r, p, r, q]):
            continue
        if not proof.statements.checker.check_ncoll([a, b, c]):
            continue

        mapping = dict(zip("ABCPQR", [a, b, c, p, q, r]))
        record.add((a, b, c, p, q, r))
        yield mapping


def match_eqangle6_eqangle6_ncoll_simtri2(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle6 B A B C Q R Q P, eqangle6 C A C B R Q R P, ncoll A B C => simtri2 A B C P Q R."""
    enums = g_matcher(Predicate.EQANGLE6.value)

    record = set()
    for b, a, b, c, q, r, q, p in enums:
        if (a, b, c) == (p, q, r):
            continue
        if any([x in record for x in rotate_simtri(a, b, c, p, q, r)]):
            continue
        if not proof.statements.checker.check_eqangle([c, a, c, b, r, q, r, p]):
            continue
        if not proof.statements.checker.check_ncoll([a, b, c]):
            continue

        mapping = dict(zip("ABCPQR", [a, b, c, p, q, r]))
        record.add((a, b, c, p, q, r))
        yield mapping


def match_eqangle6_eqangle6_ncoll_cong_contri(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle6 B A B C Q P Q R, eqangle6 C A C B R P R Q, ncoll A B C, cong A B P Q => contri A B C P Q R."""
    enums = g_matcher(Predicate.EQANGLE6.value)

    record = set()
    for b, a, b, c, q, p, q, r in enums:
        if not proof.statements.checker.check_cong([a, b, p, q]):
            continue
        if (a, b, c) == (p, q, r):
            continue
        if any([x in record for x in rotate_contri(a, b, c, p, q, r)]):
            continue
        if not proof.statements.checker.check_eqangle([c, a, c, b, r, p, r, q]):
            continue

        if not proof.statements.checker.check_ncoll([a, b, c]):
            continue

        mapping = dict(zip("ABCPQR", [a, b, c, p, q, r]))
        record.add((a, b, c, p, q, r))
        yield mapping


def match_eqratio6_eqratio6_ncoll_cong_contri(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqratio6 B A B C Q P Q R, eqratio6 C A C B R P R Q, ncoll A B C, cong A B P Q => contri* A B C P Q R."""
    enums = g_matcher(Predicate.EQRATIO6.value)

    record = set()
    for b, a, b, c, q, p, q, r in enums:
        if not proof.statements.checker.check_cong([a, b, p, q]):
            continue
        if (a, b, c) == (p, q, r):
            continue
        if any([x in record for x in rotate_contri(a, b, c, p, q, r)]):
            continue
        if not proof.statements.checker.check_eqratio([c, a, c, b, r, p, r, q]):
            continue

        if not proof.statements.checker.check_ncoll([a, b, c]):
            continue

        mapping = dict(zip("ABCPQR", [a, b, c, p, q, r]))
        record.add((a, b, c, p, q, r))
        yield mapping


def match_eqangle6_eqangle6_ncoll_cong_contri2(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle6 B A B C Q R Q P, eqangle6 C A C B R Q R P, ncoll A B C, cong A B P Q => contri2 A B C P Q R."""
    enums = g_matcher(Predicate.EQANGLE6.value)

    record = set()
    for b, a, b, c, q, r, q, p in enums:
        if not proof.statements.checker.check_cong([a, b, p, q]):
            continue
        if (a, b, c) == (p, q, r):
            continue
        if any([x in record for x in rotate_contri(a, b, c, p, q, r)]):
            continue
        if not proof.statements.checker.check_eqangle([c, a, c, b, r, q, r, p]):
            continue
        if not proof.statements.checker.check_ncoll([a, b, c]):
            continue

        mapping = dict(zip("ABCPQR", [a, b, c, p, q, r]))
        record.add((a, b, c, p, q, r))
        yield mapping


def match_eqratio6_coll_ncoll_eqangle6(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqratio6 d b d c a b a c, coll d b c, ncoll a b c => eqangle6 a b a d a d a c."""
    records = set()
    for b, d, c in g_matcher(Predicate.COLLINEAR.value):
        for a in proof.symbols_graph.all_points():
            if proof.statements.checker.check_coll([a, b, c]):
                continue
            if (a, b, d, c) in records or (a, c, d, b) in records:
                continue
            records.add((a, b, d, c))

            if proof.statements.checker.check_eqratio([d, b, d, c, a, b, a, c]):
                yield dict(zip("abcd", [a, b, c, d]))


def match_eqangle6_coll_ncoll_eqratio6(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle6 a b a d a d a c, coll d b c, ncoll a b c => eqratio6 d b d c a b a c."""
    records = set()
    for b, d, c in g_matcher(Predicate.COLLINEAR.value):
        for a in proof.symbols_graph.all_points():
            if proof.statements.checker.check_coll([a, b, c]):
                continue
            if (a, b, d, c) in records or (a, c, d, b) in records:
                continue
            records.add((a, b, d, c))

            if proof.statements.checker.check_eqangle([a, b, a, d, a, d, a, c]):
                yield dict(zip("abcd", [a, b, c, d]))


def match_eqangle6_ncoll_cyclic(
    proof: "Proof",
    g_matcher: Callable[[str], list[tuple[Point, ...]]],
    theorem: "Theorem",
) -> Generator[dict[str, Point], None, None]:
    """Match eqangle6 P A P B Q A Q B, ncoll P Q A B => cyclic A B P Q."""
    for a, b, a, c, x, y, x, z in g_matcher(Predicate.EQANGLE6.value):
        if (b, c) != (y, z) or a == x:
            continue
        if check_ncoll_numerical([x.num for x in [a, b, c, x]]):
            yield dict(zip("ABPQ", [b, c, a, x]))


def try_to_map(
    clause_enum: list[tuple["Clause", list[tuple[Point, ...]]]],
    mapping: dict[str, Point],
) -> Generator[dict[str, Point], None, None]:
    """Recursively try to match the remaining points given current mapping."""
    if not clause_enum:
        yield mapping
        return

    clause, enum = clause_enum[0]
    for points in enum:
        mpcpy = dict(mapping)

        fail = False
        for p, a in zip(points, clause.args):
            if a in mpcpy and mpcpy[a] != p or p in mpcpy and mpcpy[p] != a:
                fail = True
                break
            mpcpy[a] = p
            mpcpy[p] = a

        if fail:
            continue

        for m in try_to_map(clause_enum[1:], mpcpy):
            yield m


def match_generic(
    proof: "Proof", cache: "MatchCache", theorem: "Theorem"
) -> Generator[dict[str, Point], None, None]:
    """Match any generic rule that is not one of the above match_*() rules."""
    clause2enum = {}

    clauses = []
    numerical_checks = []
    for clause in theorem.premises:
        if clause.name in [
            Predicate.NON_COLLINEAR.value,
            Predicate.NON_PARALLEL.value,
            Predicate.NON_PERPENDICULAR.value,
            Predicate.SAMESIDE.value,
        ]:
            numerical_checks.append(clause)
            continue

        enum = cache(clause.name)
        if len(enum) == 0:
            return 0

        clause2enum[clause] = enum
        clauses.append((len(set(clause.args)), clause))

    clauses = sorted(clauses, key=lambda x: x[0], reverse=True)
    _, clauses = zip(*clauses)

    for mapping in try_to_map([(c, clause2enum[c]) for c in clauses], {}):
        if not mapping:
            continue

        checks_ok = True
        for check in numerical_checks:
            args = [mapping[a] for a in check.args]
            if check.name == Predicate.NON_COLLINEAR.value:
                checks_ok = proof.statements.checker.check_ncoll(args)
            elif check.name == Predicate.NON_PARALLEL.value:
                checks_ok = proof.statements.checker.check_npara(args)
            elif check.name == Predicate.NON_PERPENDICULAR.value:
                checks_ok = proof.statements.checker.check_nperp(args)
            elif check.name == Predicate.SAMESIDE.value:
                checks_ok = proof.statements.checker.check_sameside(args)
            if not checks_ok:
                break
        if not checks_ok:
            continue

        yield mapping


BUILT_IN_FNS = {
    "cong_cong_cong_cyclic": match_cong_cong_cong_cyclic,
    "cong_cong_cong_ncoll_contri*": match_cong_cong_cong_ncoll_contri,
    "cong_cong_eqangle6_ncoll_contri*": match_cong_cong_eqangle6_ncoll_contri,
    "eqangle6_eqangle6_ncoll_simtri": match_eqangle6_eqangle6_ncoll_simtri,
    "eqangle6_eqangle6_ncoll_cong_contri": (match_eqangle6_eqangle6_ncoll_cong_contri),
    "eqangle6_eqangle6_ncoll_simtri2": match_eqangle6_eqangle6_ncoll_simtri2,
    "eqangle6_eqangle6_ncoll_cong_contri2": (
        match_eqangle6_eqangle6_ncoll_cong_contri2
    ),
    "eqratio6_eqratio6_ncoll_simtri*": match_eqratio6_eqratio6_ncoll_simtri,
    "eqratio6_eqratio6_ncoll_cong_contri*": (match_eqratio6_eqratio6_ncoll_cong_contri),
    "eqangle_para": match_eqangle_para,
    "eqangle_ncoll_cyclic": match_eqangle_ncoll_cyclic,
    "eqratio6_eqangle6_ncoll_simtri*": match_eqratio6_eqangle6_ncoll_simtri,
    "eqangle_perp_perp": match_eqangle_perp_perp,
    "eqangle6_ncoll_cong": match_eqangle6_ncoll_cong,
    "perp_perp_ncoll_para": match_perp_perp_ncoll_para,
    "circle_perp_eqangle": match_circle_perp_eqangle,
    "circle_eqangle_perp": match_circle_eqangle_perp,
    "cyclic_eqangle_cong": match_cyclic_eqangle_cong,
    "midp_perp_cong": match_midp_perp_cong,
    "perp_perp_npara_eqangle": match_perp_perp_npara_eqangle,
    "cyclic_eqangle": match_cyclic_eqangle,
    "eqangle_eqangle_eqangle": match_eqangle_eqangle_eqangle,
    "eqratio_eqratio_eqratio": match_eqratio_eqratio_eqratio,
    "eqratio6_coll_ncoll_eqangle6": match_eqratio6_coll_ncoll_eqangle6,
    "eqangle6_coll_ncoll_eqratio6": match_eqangle6_coll_ncoll_eqratio6,
    "eqangle6_ncoll_cyclic": match_eqangle6_ncoll_cyclic,
}


class MatchCache:
    def __init__(self, proof: "Proof") -> None:
        self.cache = {}
        self.proof = proof

    def __call__(self, name: str) -> list[tuple[Point, ...]]:
        cached = self.cache.get(name)
        if cached is not None:
            return cached

        result = list(self.proof.statements.enumerator.all(name))
        self.cache[name] = result
        return result

    def reset(self):
        self.cache = {}


def match_one_theorem(
    proof: "Proof",
    theorem: "Theorem",
    cache: Optional[MatchCache] = None,
    goals: Optional[list[Construction]] = None,
    max_mappings: int = 50_000,
) -> list[Mapping]:
    """Match all instances of a single theorem (rule)."""
    if cache is None:
        cache = MatchCache(proof)

    name = theorem.name
    if name.split("_")[-1] in [
        Predicate.COMPUTE_ANGLE.value,
        Predicate.COMPUTE_RATIO.value,
        Predicate.FIX_L.value,
        Predicate.FIX_C.value,
        Predicate.FIX_B.value,
        Predicate.FIX_T.value,
        Predicate.FIX_P.value,
    ]:
        if goals and all(goal.name != name for goal in goals):
            return []

    if theorem.name in BUILT_IN_FNS:
        mps = BUILT_IN_FNS[theorem.name](proof, cache, theorem)
    else:
        mps = match_generic(proof, cache, theorem)

    mappings = []
    for mp in mps:
        mappings.append(mp)
        if len(mappings) > max_mappings:  # cap branching at this number.
            break

    return mappings
