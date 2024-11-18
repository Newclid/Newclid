from __future__ import annotations
from collections import defaultdict
from typing import TYPE_CHECKING, Generator

from newclid.combinatorics import (
    all_4points,
    all_8points,
    arrangement_pairs,
    cross_product,
    permutations_pairs,
    permutations_quadruplets,
    permutations_triplets,
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
)
from newclid.predicates import Predicate


if TYPE_CHECKING:
    from newclid.symbols_graph import SymbolsGraph
    from newclid.statements.checker import StatementChecker


class StatementsEnumerator:
    def __init__(
        self,
        symbols_graph: "SymbolsGraph",
        statements_checker: "StatementChecker",
    ) -> None:
        self.symbols_graph = symbols_graph
        self.statements_checker = statements_checker

    def all(
        self, predicate_name: str | Predicate
    ) -> Generator[tuple[Point, ...], None, None]:
        """Enumerate all instances of a certain predicate."""

        try:
            predicate = Predicate(predicate_name)
        except ValueError:
            raise ValueError(f"Unrecognize predicate: {predicate_name}")

        if predicate in [
            Predicate.NON_COLLINEAR,
            Predicate.NON_PARALLEL,
            Predicate.NON_PERPENDICULAR,
        ]:
            return []

        PREDICATE_TO_METHOD = {
            Predicate.COLLINEAR: self._all_colls,
            Predicate.PARALLEL: self._all_paras,
            Predicate.PERPENDICULAR: self._all_perps,
            Predicate.MIDPOINT: self._all_midps,
            Predicate.CONGRUENT: self._all_congs,
            Predicate.CIRCLE: self._all_circles,
            Predicate.CYCLIC: self._all_cyclics,
            Predicate.EQANGLE: self._all_eqangles_8points,
            Predicate.EQANGLE6: self._all_eqangles_6points,
            Predicate.EQRATIO: self._all_eqratios_8points,
            Predicate.EQRATIO6: self._all_eqratios_6points,
        }

        if predicate not in PREDICATE_TO_METHOD:
            raise NotImplementedError(
                f"Enumerator not implemented for predicate: {predicate_name}"
            )

        return PREDICATE_TO_METHOD[predicate]()

    def all_eqangles_distinct_linepairss(
        self,
    ) -> Generator[tuple[Line, ...], None, None]:
        """No eqangles betcause para-para, or para-corresponding, or same."""

        for measure in self.symbols_graph.type2nodes[AngleValue]:
            angs = measure.neighbors(Angle)
            line_pairss = []
            for ang in angs:
                d1, d2 = ang.directions
                if d1 is None or d2 is None:
                    continue
                l1s = d1.neighbors(Line)
                l2s = d2.neighbors(Line)
                # Any pair in this is para-para.
                para_para = list(cross_product(l1s, l2s))
                line_pairss.append(para_para)

            for pairs1, pairs2 in arrangement_pairs(line_pairss):
                for pair1, pair2 in cross_product(pairs1, pairs2):
                    (l1, l2), (l3, l4) = pair1, pair2
                    yield l1, l2, l3, l4

    def _all_eqangles_8points(self) -> Generator[tuple[Point, ...], None, None]:
        """List all sets of 8 points that make two equal angles."""
        # Case 1: (l1-l2) = (l3-l4), including because l1//l3, l2//l4 (para-para)
        angss = []
        for measure in self.symbols_graph.type2nodes[AngleValue]:
            angs = measure.neighbors(Angle)
            angss.append(angs)

        # include the angs that do not have any measure.
        angss.extend(
            [[ang] for ang in self.symbols_graph.type2nodes[Angle] if ang.val is None]
        )

        line_pairss = []
        for angs in angss:
            line_pairs = set()
            for ang in angs:
                d1, d2 = ang.directions
                if d1 is None or d2 is None:
                    continue
                l1s = d1.neighbors(Line)
                l2s = d2.neighbors(Line)
                line_pairs.update(set(cross_product(l1s, l2s)))
            line_pairss.append(line_pairs)

        # include (d1, d2) in which d1 does not have any angles.
        noang_ds = [
            d
            for d in self.symbols_graph.type2nodes[Direction]
            if not d.neighbors(Angle)
        ]

        for d1 in noang_ds:
            for d2 in self.symbols_graph.type2nodes[Direction]:
                if d1 == d2:
                    continue
                l1s = d1.neighbors(Line)
                l2s = d2.neighbors(Line)
                if len(l1s) < 2 and len(l2s) < 2:
                    continue
                line_pairss.append(set(cross_product(l1s, l2s)))
                line_pairss.append(set(cross_product(l2s, l1s)))

        # Case 2: d1 // d2 => (d1-d3) = (d2-d3)
        # include lines that does not have any direction.
        nodir_ls = [
            line for line in self.symbols_graph.type2nodes[Line] if line.val is None
        ]

        for line in nodir_ls:
            for d in self.symbols_graph.type2nodes[Direction]:
                l1s = d.neighbors(Line)
                if len(l1s) < 2:
                    continue
                l2s = [line]
                line_pairss.append(set(cross_product(l1s, l2s)))
                line_pairss.append(set(cross_product(l2s, l1s)))

        record = set()
        for line_pairs in line_pairss:
            for pair1, pair2 in permutations_pairs(list(line_pairs)):
                (l1, l2), (l3, l4) = pair1, pair2
                if l1 == l2 or l3 == l4:
                    continue
                if (l1, l2) == (l3, l4):
                    continue
                if (l1, l2, l3, l4) in record:
                    continue
                record.add((l1, l2, l3, l4))
                for a, b, c, d, e, f, g, h in all_8points(l1, l2, l3, l4):
                    yield (a, b, c, d, e, f, g, h)

        for a, b, c, d, e, f, g, h in self._all_eqangle_same_lines():
            yield a, b, c, d, e, f, g, h

    def _all_eqangles_6points(self) -> Generator[tuple[Point, ...], None, None]:
        """List all sets of 6 points that make two equal angles."""
        record = set()
        for a, b, c, d, e, f, g, h in self._all_eqangles_8points():
            if (
                a not in (c, d)
                and b not in (c, d)
                or e not in (g, h)
                and f not in (g, h)
            ):
                continue

            if b in (c, d):
                a, b = b, a  # now a in c, d
            if f in (g, h):
                e, f = f, e  # now e in g, h
            if a == d:
                c, d = d, c  # now a == c
            if e == h:
                g, h = h, g  # now e == g
            if (a, b, c, d, e, f, g, h) in record:
                continue
            record.add((a, b, c, d, e, f, g, h))
            yield a, b, c, d, e, f, g, h  # where a==c, e==g

    def _all_paras(self) -> Generator[tuple[Point, ...], None, None]:
        for d in self.symbols_graph.type2nodes[Direction]:
            for l1, l2 in permutations_pairs(d.neighbors(Line)):
                for a, b, c, d in all_4points(l1, l2):
                    yield a, b, c, d

    def _all_perps(self) -> Generator[tuple[Point, ...], None, None]:
        for ang in self.symbols_graph.vhalfpi.neighbors(Angle):
            d1, d2 = ang.directions
            if d1 is None or d2 is None:
                continue
            if d1 == d2:
                continue
            for l1, l2 in cross_product(d1.neighbors(Line), d2.neighbors(Line)):
                for a, b, c, d in all_4points(l1, l2):
                    yield a, b, c, d

    def _all_congs(self) -> Generator[tuple[Point, ...], None, None]:
        for lenght in self.symbols_graph.type2nodes[Length]:
            for s1, s2 in permutations_pairs(lenght.neighbors(Segment)):
                (a, b), (c, d) = s1.points, s2.points
                for x, y in [(a, b), (b, a)]:
                    for m, n in [(c, d), (d, c)]:
                        yield x, y, m, n

    def _all_eqratios_8points(self) -> Generator[tuple[Point, ...], None, None]:
        """List all sets of 8 points that make two equal ratios."""
        ratss = []
        for value in self.symbols_graph.type2nodes[RatioValue]:
            rats = value.neighbors(Ratio)
            ratss.append(rats)

        # include the rats that do not have any val.
        ratss.extend(
            [[rat] for rat in self.symbols_graph.type2nodes[Ratio] if rat.val is None]
        )

        seg_pairss = []
        for rats in ratss:
            seg_pairs = set()
            for rat in rats:
                l1, l2 = rat.lengths
                if l1 is None or l2 is None:
                    continue
                s1s = l1.neighbors(Segment)
                s2s = l2.neighbors(Segment)
                seg_pairs.update(cross_product(s1s, s2s))
            seg_pairss.append(seg_pairs)

        # include (l1, l2) in which l1 does not have any ratio.
        norat_ls = [
            lenght
            for lenght in self.symbols_graph.type2nodes[Length]
            if not lenght.neighbors(Ratio)
        ]

        for l1 in norat_ls:
            for l2 in self.symbols_graph.type2nodes[Length]:
                if l1 == l2:
                    continue
                s1s = l1.neighbors(Segment)
                s2s = l2.neighbors(Segment)
                if len(s1s) < 2 and len(s2s) < 2:
                    continue
                seg_pairss.append(set(cross_product(s1s, s2s)))
                seg_pairss.append(set(cross_product(s2s, s1s)))

        # include Seg that does not have any Length.
        nolen_ss = [s for s in self.symbols_graph.type2nodes[Segment] if s.val is None]

        for seg in nolen_ss:
            for lenght in self.symbols_graph.type2nodes[Length]:
                s1s = lenght.neighbors(Segment)
                if len(s1s) == 1:
                    continue
                s2s = [seg]
                seg_pairss.append(set(cross_product(s1s, s2s)))
                seg_pairss.append(set(cross_product(s2s, s1s)))

        record = set()
        for seg_pairs in seg_pairss:
            for pair1, pair2 in permutations_pairs(list(seg_pairs)):
                (s1, s2), (s3, s4) = pair1, pair2
                if s1 == s2 or s3 == s4:
                    continue
                if (s1, s2) == (s3, s4):
                    continue
                if (s1, s2, s3, s4) in record:
                    continue
                record.add((s1, s2, s3, s4))
                a, b = s1.points
                c, d = s2.points
                e, f = s3.points
                g, h = s4.points

                for x, y in [(a, b), (b, a)]:
                    for z, t in [(c, d), (d, c)]:
                        for m, n in [(e, f), (f, e)]:
                            for p, q in [(g, h), (h, g)]:
                                yield (x, y, z, t, m, n, p, q)

        segss = []
        # finally the list of ratios that is equal to 1.0
        for length in self.symbols_graph.type2nodes[Length]:
            segs = length.neighbors(Segment)
            segss.append(tuple(segs))

        segs_pair = list(permutations_pairs(list(segss)))
        segs_pair += list(zip(segss, segss))
        for segs1, segs2 in segs_pair:
            for s1, s2 in permutations_pairs(list(segs1)):
                for s3, s4 in permutations_pairs(list(segs2)):
                    if (s1, s2) == (s3, s4) or (s1, s3) == (s2, s4):
                        continue
                    if (s1, s2, s3, s4) in record:
                        continue
                    record.add((s1, s2, s3, s4))
                    a, b = s1.points
                    c, d = s2.points
                    e, f = s3.points
                    g, h = s4.points

                    for x, y in [(a, b), (b, a)]:
                        for z, t in [(c, d), (d, c)]:
                            for m, n in [(e, f), (f, e)]:
                                for p, q in [(g, h), (h, g)]:
                                    yield (x, y, z, t, m, n, p, q)

    def _all_eqratios_6points(self) -> Generator[tuple[Point, ...], None, None]:
        """List all sets of 6 points that make two equal angles."""
        record = set()
        for a, b, c, d, e, f, g, h in self._all_eqratios_8points():
            if (
                a not in (c, d)
                and b not in (c, d)
                or e not in (g, h)
                and f not in (g, h)
            ):
                continue
            if b in (c, d):
                a, b = b, a
            if f in (g, h):
                e, f = f, e
            if a == d:
                c, d = d, c
            if e == h:
                g, h = h, g
            if (a, b, c, d, e, f, g, h) in record:
                continue
            record.add((a, b, c, d, e, f, g, h))
            yield a, b, c, d, e, f, g, h  # now a==c, e==g

    def _all_cyclics(self) -> Generator[tuple[Point, ...], None, None]:
        for c in self.symbols_graph.type2nodes[Circle]:
            for x, y, z, t in permutations_quadruplets(c.neighbors(Point)):
                yield x, y, z, t

    def _all_colls(self) -> Generator[tuple[Point, ...], None, None]:
        for line in self.symbols_graph.type2nodes[Line]:
            for x, y, z in permutations_triplets(line.neighbors(Point)):
                yield x, y, z

    def _all_midps(self) -> Generator[tuple[Point, ...], None, None]:
        for line in self.symbols_graph.type2nodes[Line]:
            for a, b, c in permutations_triplets(line.neighbors(Point)):
                if self.statements_checker.check_cong([a, b, a, c]):
                    yield a, b, c

    def _all_circles(self) -> Generator[tuple[Point, ...], None, None]:
        for lenght in self.symbols_graph.type2nodes[Length]:
            p2p = defaultdict(list)
            for s in lenght.neighbors(Segment):
                a, b = s.points
                p2p[a].append(b)
                p2p[b].append(a)
            for p, ps in p2p.items():
                if len(ps) >= 3:
                    for a, b, c in permutations_triplets(ps):
                        yield p, a, b, c

    def _all_eqangle_same_lines(self) -> Generator[tuple[Point, ...], None, None]:
        for l1, l2 in permutations_pairs(self.symbols_graph.type2nodes[Line]):
            for a, b, c, d, e, f, g, h in all_8points(l1, l2, l1, l2):
                if (a, b, c, d) != (e, f, g, h):
                    yield a, b, c, d, e, f, g, h
