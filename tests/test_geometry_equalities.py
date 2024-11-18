"""Unit tests for geometry.py."""

import pytest_check as check

from newclid.dependencies.why_predicates import _why_equal
from newclid.geometry import Length, Segment


class TestGeometry:
    def _setup_equality_example(self):
        # Create 4 nodes a, b, c, d
        # and their lengths
        a = Segment("a")
        la = Length("l(a)")
        a.connect_to(la)
        la.connect_to(a)

        b = Segment("b")
        lb = Length("l(b)")
        b.connect_to(lb)
        lb.connect_to(b)

        c = Segment("c")
        lc = Length("l(c)")
        c.connect_to(lc)
        lc.connect_to(c)

        d = Segment("d")
        ld = Length("l(d)")
        d.connect_to(ld)
        ld.connect_to(d)

        # Now let la=lb, lb=lc, la=lc, lc=ld
        la.merge([lb], "fact1")
        lb.merge([lc], "fact2")
        la.merge([lc], "fact3")
        lc.merge([ld], "fact4")
        return a, b, c, d, la, lb, lc, ld

    def test_merged_node_representative(self):
        _, _, _, _, la, lb, lc, ld = self._setup_equality_example()

        # all nodes are now represented by la.
        check.equal(la.rep(), la)
        check.equal(lb.rep(), la)
        check.equal(lc.rep(), la)
        check.equal(ld.rep(), la)

    def test_merged_node_equivalence(self):
        _, _, _, _, la, lb, lc, ld = self._setup_equality_example()
        # all la, lb, lc, ld are equivalent
        check.equal(set(la.equivs()), {la, lb, lc, ld})
        check.equal(set(lb.equivs()), {la, lb, lc, ld})
        check.equal(set(lc.equivs()), {la, lb, lc, ld})
        check.equal(set(ld.equivs()), {la, lb, lc, ld})

    def test_bfs_for_equality_transitivity(self):
        a, _, _, d, _, _, _, _ = self._setup_equality_example()

        # check that a==d because fact3 & fact4, not fact1 & fact2
        check.equal(set(_why_equal(a, d)), {"fact3", "fact4"})
