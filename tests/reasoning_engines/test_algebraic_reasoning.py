import pytest
import pytest_check as check
from newclid.predicates import Predicate
from newclid.reasoning_engines.algebraic_reasoning.algebraic_manipulator import (
    AlgebraicManipulator,
)
import newclid.reasoning_engines.algebraic_reasoning.geometric_tables as geometric_tables
from newclid.dependencies.dependency import Dependency, Reason
from newclid.dependencies.dependency_building import DependencyBody
from newclid.numerical.check import clock
from newclid.api import GeometricSolverBuilder
from newclid.statements.statement import Statement
from newclid.symbols_graph import SymbolsGraphBuilder
from tests.fixtures import build_until_works


class TestAR:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.solver_builder = GeometricSolverBuilder()

    def test_update_groups(self):
        """Test for update_groups."""
        groups1 = [{1, 2}, {3, 4, 5}, {6, 7}]
        groups2 = [{2, 3, 8}, {9, 10, 11}]

        _, links, history = geometric_tables.update_groups(groups1, groups2)
        check.equal(
            history,
            [
                [{1, 2, 3, 4, 5, 8}, {6, 7}],
                [{1, 2, 3, 4, 5, 8}, {6, 7}, {9, 10, 11}],
            ],
        )
        check.equal(links, [(2, 3), (3, 8), (9, 10), (10, 11)])

        groups1 = [{1, 2}, {3, 4}, {5, 6}, {7, 8}]
        groups2 = [{2, 3, 8, 9, 10}, {3, 6, 11}]

        _, links, history = geometric_tables.update_groups(groups1, groups2)
        check.equal(
            history,
            [
                [{1, 2, 3, 4, 7, 8, 9, 10}, {5, 6}],
                [{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}],
            ],
        )
        check.equal(links, [(2, 3), (3, 8), (8, 9), (9, 10), (3, 6), (6, 11)])

        groups1 = []
        groups2 = [{1, 2}, {3, 4}, {5, 6}, {2, 3}]

        _, links, history = geometric_tables.update_groups(groups1, groups2)
        check.equal(
            history,
            [
                [{1, 2}],
                [{1, 2}, {3, 4}],
                [{1, 2}, {3, 4}, {5, 6}],
                [{1, 2, 3, 4}, {5, 6}],
            ],
        )
        check.equal(links, [(1, 2), (3, 4), (5, 6), (2, 3)])

    def test_generic_table_simple(self):
        tb = geometric_tables.Table()

        # If a-b = b-c & d-a = c-d
        tb.add_eq4("a", "b", "b", "c", "fact1")
        tb.add_eq4("d", "a", "c", "d", "fact2")
        tb.add_eq4("x", "y", "z", "t", "fact3")  # distractor fact

        # Then b=d, because {fact1, fact2} but not fact3.
        result = list(tb.get_all_eqs_and_why())
        check.is_in(("b", "d", ["fact1", "fact2"]), result)

    def test_angle_table_inbisector_exbisector(self):
        """Test that AR can figure out bisector & ex-bisector are perpendicular."""
        # Load the scenario that we have cd is bisector of acb and
        # ce is the ex-bisector of acb.

        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = incenter d a b c; "
            "e = excenter e a b c "
            "? perp d c c e"
        ).build()
        proof = solver.proof_state

        # Create an external angle table:
        tb = geometric_tables.AngleTable(
            "pi", solver.proof_state.symbols_graph.get_or_create_const_ang(180, 1)
        )

        # Add bisector & ex-bisector facts into the table:
        ca, cd, cb, ce = proof.symbols_graph.names2nodes(
            ["d(ac)", "d(cd)", "d(bc)", "d(ce)"]
        )
        tb.add_eqangle(ca, cd, cd, cb, "fact1")
        tb.add_eqangle(ce, ca, cb, ce, "fact2")

        # Add a distractor fact to make sure traceback does not include this fact
        ab = proof.symbols_graph.names2nodes(["d(ab)"])[0]
        tb.add_eqangle(ab, cb, cb, ca, "fact3")

        # Check for all new equalities
        result = list(tb.get_all_eqs_and_why())

        # halfpi is represented as a tuple (1, 2)
        halfpi = geometric_tables.Coef(0.5)

        # check that cd-ce == halfpi and this is because fact1 & fact2, not fact3
        check.equal(
            result,
            [
                (cd, ce, halfpi, ["fact1", "fact2"]),
                (ce, cd, halfpi, ["fact1", "fact2"]),
            ],
        )

    def test_angle_table_equilateral_triangle(self):
        """Test that AR can figure out triangles with 3 equal angles => each is pi/3."""
        # Load an equaliteral scenario
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = ieq_triangle " "? cong a b a c"
        ).build()
        proof = solver.proof_state

        # Add two eqangles facts because ieq_triangle only add congruent sides
        a, b, c = proof.symbols_graph.names2nodes("abc")
        proof.statements.adder._add_eqangle(
            [a, b, b, c, b, c, c, a], DependencyBody(Reason("None"), why=[])
        )
        proof.statements.adder._add_eqangle(
            [b, c, c, a, c, a, a, b], DependencyBody(Reason("None"), why=[])
        )

        # Create an external angle table:
        tb = geometric_tables.AngleTable(
            "pi", solver.proof_state.symbols_graph.get_or_create_const_ang(180, 1)
        )

        # Add the fact that there are three equal angles
        ab, bc, ca = proof.symbols_graph.names2nodes(["d(ab)", "d(bc)", "d(ac)"])
        tb.add_eqangle(ab, bc, bc, ca, "fact1")
        tb.add_eqangle(bc, ca, ca, ab, "fact2")

        # Now check for all new equalities
        result = list(tb.get_all_eqs_and_why())
        result = [(x.name, y.name, z, t) for x, y, z, t in result]

        # 1/3 pi is represented as a tuple angle_60
        angle_60 = geometric_tables.Coef(1 / 3)
        angle_120 = geometric_tables.Coef(2 / 3)

        is_clockwise = clock(a.num, b.num, c.num) > 0

        if not is_clockwise:
            expected = [
                ("d(bc)", "d(ac)", angle_120, ["fact1", "fact2"]),
                ("d(ab)", "d(bc)", angle_120, ["fact1", "fact2"]),
                ("d(ac)", "d(ab)", angle_120, ["fact1", "fact2"]),
                ("d(ac)", "d(bc)", angle_60, ["fact1", "fact2"]),
                ("d(bc)", "d(ab)", angle_60, ["fact1", "fact2"]),
                ("d(ab)", "d(ac)", angle_60, ["fact1", "fact2"]),
            ]
        else:
            expected = [
                ("d(bc)", "d(ac)", angle_60, ["fact1", "fact2"]),
                ("d(ab)", "d(bc)", angle_60, ["fact1", "fact2"]),
                ("d(ac)", "d(ab)", angle_60, ["fact1", "fact2"]),
                ("d(ac)", "d(bc)", angle_120, ["fact1", "fact2"]),
                ("d(bc)", "d(ab)", angle_120, ["fact1", "fact2"]),
                ("d(ab)", "d(ac)", angle_120, ["fact1", "fact2"]),
            ]

        # check that angles constants are created and figured out:
        check.equal(result, expected)

    def test_checking_orthocenter_consequence_aux(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle; d = on_tline d b a c, on_tline d c a b; e = on_line e a c, on_line e b d; f = on_tline f c b c ? para a d f c",
            translate=False,
        ).build()
        success = solver.run()
        check.is_true(success)

    @pytest.mark.skip
    def test_geometric_ratios(self):  # midpoint not added
        solver = self.solver_builder.load_problem_from_txt(
            "a b = segment a b; m = midpoint m a b ? rconst a m b m 1/1",
            translate=False,
        ).build()
        success = solver.run()
        check.is_true(success)

    def test_concatenating_ratios(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b = segment a b; c = free c; d = rconst a b c d 2/1; e = rconst c d a e 2/1 ? rconst a b a e 4/1",
            translate=False,
        ).build()
        success = solver.run()
        check.is_true(success)

    def test_lconst_eqratio_check(self):
        solver = self.solver_builder.load_problem_from_file(
            "problems_datasets/examples.txt", "lconst_eqratio_check", translate=False
        ).build()
        success = solver.run()
        check.is_true(success)

    @pytest.mark.xfail
    def test_lconst_cong_lconst_check(self):
        solver = self.solver_builder.load_problem_from_file(
            "problems_datasets/examples.txt", "cong_lconst_check", translate=False
        ).build()
        success = solver.run()
        check.is_true(success)

    def test_rconst_lconst_check(self):
        solver = self.solver_builder.load_problem_from_file(
            "problems_datasets/examples.txt", "rconst_lconst_check", translate=False
        ).build()
        success = solver.run()
        check.is_true(success)

    def test_incenter_excenter_touchpoints(self):
        """Test that AR can figure out incenter/excenter touchpoints are equidistant to midpoint."""
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d1 d2 d3 d = incenter2 a b c; "
            "e1 e2 e3 e = excenter2 a b c "
            "? perp d c c e",
            translate=False,
        ).build()
        proof = solver.proof_state

        a, b, c, ab, bc, ca, d1, d2, d3, e1, e2, e3 = proof.symbols_graph.names2nodes(
            ["a", "b", "c", "ab", "bc", "ac", "d1", "d2", "d3", "e1", "e2", "e3"]
        )

        # Create an external distance table:
        tb = geometric_tables.DistanceTable()

        # DD can figure out the following facts,
        # we manually add them to AR.
        tb.add_cong(ab, ca, a, d3, a, d2, "fact1")
        tb.add_cong(ab, ca, a, e3, a, e2, "fact2")
        tb.add_cong(ca, bc, c, d2, c, d1, "fact5")
        tb.add_cong(ca, bc, c, e2, c, e1, "fact6")
        tb.add_cong(bc, ab, b, d1, b, d3, "fact3")
        tb.add_cong(bc, ab, b, e1, b, e3, "fact4")

        # Now we check whether tb has figured out that
        # distance(b, d1) == distance(e1, c)

        # linear comb exprssion of each variables:
        b = tb.v2e["bc:b"]
        c = tb.v2e["bc:c"]
        d1 = tb.v2e["bc:d1"]
        e1 = tb.v2e["bc:e1"]

        check.equal(geometric_tables.minus(d1, b), geometric_tables.minus(c, e1))

    def test_two_triangles(self):
        """Test that AR can add angles through adjacent triangles."""
        defs = [
            "segment a b",
            "",
            " =",
            "a : ; b :",
            "segment",
            "",
            "s_angle a b x y",
            "x : a b x",
            "a b = diff a b",
            "x : s_angle a b x y",
            "s_angle a b y",
            "",
            "on_line x a b",
            "x : x a b",
            "a b = diff a b",
            "x : coll x a b",
            "line a b",
            "",
        ]
        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b = segment a b; "
                "c = s_angle a b c 150o, s_angle b a c 30o; "
                "d = s_angle c a d 20o, on_line d c b "
                "? aconst b c a d 5pi/9"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_paper_ratio_chasing(self):
        """Example of ratio chasing given in the original AG paper."""
        defs = [
            "triangle a b c",
            "",
            " =",
            "a : ; b : ; c :",
            "triangle",
            "",
            "midpoint x a b",
            "x : a b",
            "a b = diff a b",
            "x : coll x a b, cong x a x b",
            "midp a b",
            "",
            "on_line x a b",
            "x : x a b",
            "a b = diff a b",
            "x : coll x a b",
            "line a b",
            "",
            "angle_bisector x a b c",
            "x : a b c x",
            "a b c = ncoll a b c",
            "x : eqangle b a b x b x b c",
            "bisect a b c",
            "",
            "on_pline x a b c",
            "x : x a b c",
            "a b c = diff b c, ncoll a b c",
            "x : para x a b c",
            "pline a b c",
            "",
        ]
        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b c = triangle a b c; "
                "d = midpoint d a c; "
                "e = angle_bisector e b a c, on_line e b d; "
                "f = on_pline f b e c, on_line f a c "
                "? cong f c a b"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_paper_angle_chasing(self):
        """Example of angle chasing given in the original AG paper."""
        defs = [
            "triangle a b c",
            "",
            " =",
            "a : ; b : ; c :",
            "triangle",
            "",
            "angle_bisector x a b c",
            "x : a b c x",
            "a b c = ncoll a b c",
            "x : eqangle b a b x b x b c",
            "bisect a b c",
            "",
            "on_line x a b",
            "x : x a b",
            "a b = diff a b",
            "x : coll x a b",
            "line a b",
            "",
            "on_circum x a b c",
            "x : a b c",
            "a b c = ncoll a b c",
            "x : cyclic a b c x",
            "cyclic a b c",
            "",
        ]
        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b c = triangle a b c; "
                "d = on_circum d a b c; "
                "e = on_line e a d, on_line e b c; "
                "f = on_line f a b, on_line f c d; "
                "x = angle_bisector x a e b, angle_bisector x a f d "
                "? perp e x x f"
            )
        )
        success = solver.run()
        check.is_true(success)

    @pytest.mark.skip
    def test_paper_distance_chasing(self):
        """Example of distance chasing given in the original AG paper."""
        defs = [
            "triangle a b c",
            "",
            " =",
            "a : ; b : ; c :",
            "triangle",
            "",
            "incenter2 x y z i a b c",
            "i : a b c, x : i b c, y : i c a, z : i a b",
            "a b c = ncoll a b c",
            "i : eqangle a b a i a i a c, eqangle c a c i c i c b;"
            " eqangle b c b i b i b a;"
            " x : coll x b c, perp i x b c;"
            " y : coll y c a, perp i y c a;"
            " z : coll z a b, perp i z a b; "
            "cong i x i y, cong i y i z",
            "incenter2 a b c",
            "",
            "excenter2 x y z i a b c",
            "i : a b c, x : i b c, y : i c a, z : i a b",
            "a b c = ncoll a b c",
            "i : eqangle a b a i a i a c, eqangle c a c i c i c b;"
            " eqangle b c b i b i b a;"
            " x : coll x b c, perp i x b c;"
            " y : coll y c a, perp i y c a;"
            " z : coll z a b, perp i z a b; "
            "cong i x i y, cong i y i z",
            "excenter2 a b c",
            "",
        ]
        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b c = triangle a b c; "
                "f g e d = incenter2 f g e d a b c; "
                "j k i h = excenter2 j k i h a b c "
                "? cong c j f b"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_lconst_from_ratio_lconst(self):
        point_names = ["a", "b", "c", "d", "e", "f"]
        lengths = ["2", "5"]

        symbols_graph = (
            SymbolsGraphBuilder()
            .with_points_named(point_names)
            .with_lengths(lengths)
            .build()
        )
        a, b, c, d, e, f = symbols_graph.names2nodes(point_names)
        l2, l5 = symbols_graph.names2nodes(lengths)

        ar = AlgebraicManipulator(symbols_graph)

        dependencies = [
            Dependency(Statement(Predicate.EQRATIO, (a, b, b, c, d, e, e, f)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (a, b, l2)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (b, c, l5)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (d, e, l2)), why=[]),
        ]

        for dependency in dependencies:
            ar.ingest(dependency)

        derivations = ar.derive_ratio_algebra()
        check.is_true(
            any(
                hash(Statement(Predicate.CONSTANT_LENGTH, (f, e, l5)))
                == hash(dep.statement)
                for dep in derivations
            )
        )
