import numpy as np
import pytest
from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder


class TestConstants:
    @pytest.fixture(autouse=True)
    def setUpClass(self):
        self.rng = np.random.default_rng(233)
        self.solver_builder = GeometricSolverBuilder(rng=self.rng)
        self.problem_builder = JGEXProblemBuilder(rng=self.rng)

    def test_aconst_deg(self):
        """Should be able to prescribe and check a constant angle in degree"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; c = free c; x = aconst a b c x 63o; y = aconst a b c y 153o ? aconst c x c y 90o",
            ).build()
        )
        success = solver.run()
        assert success

    @pytest.mark.skip(reason="acompute is not supported by Yuclid")
    def test_acompute(self):
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; c = free c; x = aconst a b c x 63o; y = aconst a b c y 153o ? acompute c x c y",
            ).build()
        )
        success = solver.run()
        assert success

    def test_aconst_pi_frac(self):
        """Should be able to prescribe and check a constant angle as pi fraction"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; "
                "c = free c; "
                "x = aconst a b c x 7pi/20; "
                "y = aconst a b c y 17pi/20 "
                "? aconst c x c y 1pi/2"
            ).build()
        )
        success = solver.run()
        assert success

    def test_s_angle_deg(self):
        """Should be able to prescribe and check a constant s_angle in degree"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; x = s_angle a b x 63o; y = s_angle a b y 153o ? aconst x b b y 90o"
            ).build()
        )
        success = solver.run()
        assert success

    def test_s_angle_deg_not_perp(self):
        """Should be able to prescribe and check a constant s_angle in degree"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; x = s_angle a b x 63o; y = s_angle a b y 143o ? aconst x b b y 80o",
            ).build()
        )
        success = solver.run()
        assert success

    def test_s_angle_pi_frac(self):
        """Should be able to prescribe and check a constant s_angle as pi fraction"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; x = s_angle a b x 7pi/20; y = s_angle a b y 17pi/20 ? aconst x b b y 1pi/2",
            ).build()
        )
        success = solver.run()
        assert success

    def test_s_angle_in_perp_out(self):
        """Should be able to get a perp from prescribed s_angle in degree"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; x = s_angle a b x 63o; y = s_angle b a y 153o ? perp b x a y",
            ).build()
        )
        success = solver.run()
        assert success

    def test_s_angle_in_aconst_out(self):
        """Should be able to check aconst in radiant
        from s_angle presciption in degrees"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; x = s_angle a b x 63o; y = s_angle b a y 153o ? aconst b x a y 1pi/2"
            ).build()
        )
        success = solver.run()
        assert success

    def test_rconst(self):
        """Shoulb be able to prescribe and check a constant ratio"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; c = free c; d = rconst a b c d 3/4 ? rconst a b c d 3/4"
            ).build()
        )
        success = solver.run()
        assert success

    def test_rconst_as_theorem_conclusion(self):
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; m = midpoint m a b ? rconst m a a b 1/2",
            ).build()
        )
        success = solver.run()
        assert success

    @pytest.mark.skip
    def test_rcompute(self):
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b = segment a b; m = midpoint m a b ? rcompute m a a b",
            ).build()
        )
        success = solver.run()
        assert success

    def test_triangle12_in_rconst_out(self):
        """Should obtain a constant ratio from triangle12"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a b c = triangle12 a b c ? rconst a b a c 1/2"
            ).build()
        )
        success = solver.run()
        assert success

    def test_lconst(self):
        """Should be able to prescribe a constant lenght"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a = free a; b = lconst b a 3 ? lconst b a 3"
            ).build()
        )
        success = solver.run()
        assert success

    @pytest.mark.skip(reason="lcompute is not supported by Yuclid")
    def test_lcompute(self):
        """Should be able to prescribe a constant lenght"""
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                "a = free a; b = lconst b a 3 ? lcompute a b"
            ).build()
        )
        success = solver.run()
        assert success
