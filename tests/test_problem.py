"""Unit tests for problem.py."""

import pytest
from newclid.api import GeometricSolverBuilder


class TestProblem:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.solver_builder = GeometricSolverBuilder()

    def test_orthocenter_no_translate(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "h = on_tline h b a c, on_tline h c a b "
            "? perp a h b c",
            translate=False,
        ).build()

        # This is fed into the LM, translating from constructive to constrained:
        assert (
            solver.get_setup_string()
            == "{S} a : ; b : ; c : ; h : T a b c h 00 T a c b h 01 ? T a h b c"
        )

    def test_orthocenter_translate(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "h = on_tline h b a c, on_tline h c a b "
            "? perp a h b c",
            translate=True,
        ).build()

        # Read the txt into pr.Problem object, change h -> d to match
        # training data distribution.
        assert (
            solver.get_setup_string()
            == "{S} a : ; b : ; c : ; d : T a b c d 00 T a c b d 01 ? T a d b c"
        )

    def test_goal_free_txt(self):
        # Reading goal-free problems from txt should be invertible
        txt = "a b c = triangle a b c; h = on_tline h b a c, on_tline h c a b"
        solver = self.solver_builder.load_problem_from_txt(txt, translate=False).build()

        assert solver.get_problem_string() == txt

    def test_multiple_build(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "h = on_tline h b a c, on_tline h c a b "
            "? perp a h b c",
            translate=True,
        ).build()

        solver2 = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c",
            translate=True,
        ).build()

        # Make sure the proof_state isn't preserved between multiple calls
        assert solver.proof_state is not solver2.proof_state
