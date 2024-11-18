import pytest
import pytest_check as check

from newclid.api import GeometricSolverBuilder
from newclid.theorem import Theorem
from tests.fixtures import build_until_works


class TestConstants:
    @pytest.fixture(autouse=True)
    def setUpClass(self):
        self.solver_builder = GeometricSolverBuilder()

    def test_aconst_deg(self):
        """Should be able to prescribe and check a constant angle in degree"""
        defs = [
            "segment a b",
            "",
            " =",
            "a : ; b :",
            "segment",
            "",
            "free a",
            "a : a",
            " =",
            "a :",
            "free",
            "",
            "aconst a b c x r",
            "x : x a b c",
            "a b c = diff a b",
            "x : aconst a b c x r",
            "aconst a b c r",
            "",
        ]
        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b = segment a b; "
                "c = free c; "
                "x = aconst a b c x 63o; "
                "y = aconst a b c y 153o "
                "? aconst c x c y 90o"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_aconst_pi_frac(self):
        """Should be able to prescribe and check a constant angle as pi fraction"""
        defs = [
            "segment a b",
            "",
            " =",
            "a : ; b :",
            "segment",
            "",
            "free a",
            "a : a",
            " =",
            "a :",
            "free",
            "",
            "aconst a b c x r",
            "x : x a b c",
            "a b c = diff a b",
            "x : aconst a b c x r",
            "aconst a b c r",
            "",
        ]
        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b = segment a b; "
                "c = free c; "
                "x = aconst a b c x 7pi/20; "
                "y = aconst a b c y 17pi/20 "
                "? aconst c x c y 1pi/2"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_s_angle_deg(self):
        """Should be able to prescribe and check a constant s_angle in degree"""
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
        ]
        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b = segment a b; "
                "x = s_angle a b x 63o; "
                "y = s_angle a b y 153o "
                "? s_angle x b y 90o"
            )
        )
        success = solver.run()
        check.is_true(success)

    @pytest.mark.xfail
    def test_s_angle_deg_not_perp(self):
        """Should be able to prescribe and check a constant s_angle in degree"""
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
        ]
        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b = segment a b; "
                "x = s_angle a b x 63o; "
                "y = s_angle a b y 143o "
                "? s_angle x b y 80o"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_s_angle_pi_frac(self):
        """Should be able to prescribe and check a constant s_angle as pi fraction"""
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
        ]

        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b = segment a b; "
                "x = s_angle a b x 7pi/20; "
                "y = s_angle a b y 17pi/20 "
                "? s_angle x b y 1pi/2"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_s_angle_in_perp_out(self):
        """Should be able to get a perp from prescribed s_angle in degree"""
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
        ]

        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b = segment a b; "
                "x = s_angle a b x 63o; "
                "y = s_angle b a y 153o "
                "? perp b x a y"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_s_angle_in_aconst_out(self):
        """Should be able to check aconst in radiant
        from s_angle presciption in degrees"""
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
        ]

        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b = segment a b; "
                "x = s_angle a b x 63o; "
                "y = s_angle b a y 153o "
                "? aconst b x a y 1pi/2"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_rconst(self):
        """Shoulb be able to prescribe and check a constant ratio"""
        defs = [
            "segment a b",
            "",
            " =",
            "a : ; b :",
            "segment",
            "",
            "free a",
            "a : a",
            " =",
            "a :",
            "free",
            "",
            "rconst a b c x r",
            "x : a b c x",
            "a b c = diff a b",
            "x : rconst a b c x r",
            "rconst a b c r",
            "",
        ]
        solver = build_until_works(
            self.solver_builder.load_defs_from_txt(
                "\n".join(defs)
            ).load_problem_from_txt(
                "a b = segment a b; "
                "c = free c; "
                "d = rconst a b c d 3/4 "
                "? rconst a b c d 3/4"
            )
        )
        success = solver.run()
        check.is_true(success)

    def test_rconst_as_theorem_conclusion(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b = segment a b; m = midpoint m a b ? rconst m a a b 1/2"
        )
        solver.rules = [Theorem.from_txt("midp m a b => rconst m a a b 1/2")]
        success = solver.build().run()
        check.is_true(success)

    def test_triangle12_in_rconst_out(self):
        """Should obtain a constant ratio from triangle12"""
        defs = [
            "triangle12 a b c",
            "c : a b c",
            " =",
            "a : ; b : ; c : rconst a b a c 1/2",
            "triangle12",
            "",
        ]
        solver = build_until_works(
            self.solver_builder.load_problem_from_txt(
                "a b c = triangle12 a b c ? rconst a b a c 1/2"
            ).load_defs_from_txt("\n".join(defs))
        )
        success = solver.run()
        check.is_true(success)

    def test_lconst(self):
        """Should be able to prescribe a constant lenght"""
        solver = self.solver_builder.load_problem_from_txt(
            "a = free a; " "b = lconst b a 3 ? lconst b a 3"
        ).build()
        success = solver.run()
        check.is_true(success)
