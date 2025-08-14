import logging

import numpy as np
import pytest
from newclid.agent.follow_deductions import FollowDeductions
from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder
from py_yuclid.api_default import HEDefault
from py_yuclid.yuclid_adapter import YuclidAdapter


class TestYuclid:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.rng = np.random.default_rng(42)
        logging.getLogger("newclid.agent").setLevel(logging.WARNING)
        self.problem_builder = JGEXProblemBuilder(rng=self.rng)
        self.he_adapter = YuclidAdapter()
        self.follow_deductions = FollowDeductions(self.he_adapter)
        self.solver_builder = GeometricSolverBuilder(
            rng=self.rng, api_default=HEDefault(self.he_adapter)
        ).with_deductive_agent(self.follow_deductions)

    def test_doesnt_crash_on_problem_needing_aux_failure(self):
        self.he_adapter.problem_name = "2012_p5_without_aux"
        imo_2012_p5_without_aux = (
            "c a b = r_triangle c a b; d = foot d c a b; x = on_line x c d;"
            " k = on_line k a x, on_circle k b c; l = on_line l b x, on_circle l a c;"
            " m = on_line m a l, on_line m b k"
            " ? cong m k m l"
        )
        no_aux_solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(imo_2012_p5_without_aux).build()
        )
        success = no_aux_solver.run()
        assert not success

        imo_2012_p5_with_aux = (
            "c a b = r_triangle c a b; d = foot d c a b; x = on_line x c d;"
            " k = on_line k a x, on_circle k b c; l = on_line l b x, on_circle l a c;"
            " m = on_line m a l, on_line m b k"
            "; j = on_bline j a b, on_bline j c a; e = on_tline e d a j, on_tline e a b x"  # AUX
            " ? cong m k m l"
        )
        self.follow_deductions.reset()
        self.he_adapter.reset()
        self.he_adapter.problem_name = "2012_p5_with_aux"

        with_aux_solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(imo_2012_p5_with_aux)
            .include_auxiliary_clauses()
            .build()
        )
        success = with_aux_solver.run()
        assert success

    def test_ratio_square(self):
        self.he_adapter.problem_name = "ratio_square"
        problem_with_ratio_squares = (
            "a b c d = trapezoid a b c d; e f = square e f a b; "
            "g = parallelogram g e a b; h = eqratio h e d f g b c a; "
            "i = on_aline0 i c d e a f b g; j k = trisegment j k e d; "
            "l = on_circum l h j a, angle_bisector l e j h; m n = square m n l c; "
            "o = eqangle2 o f n k; p q = square p q e n"
        )
        solver = self.solver_builder.build(
            self.problem_builder.with_problem_from_txt(
                problem_with_ratio_squares
            ).build()
        )
        success = solver.run()
        assert success
