import pytest
import pytest_check as check

from newclid.agent.breadth_first_search import BFSDD, BFSDDAR
from newclid.api import GeometricSolverBuilder


class TestDD:
    @pytest.fixture(autouse=True)
    def setUpClass(self):
        self.solver_builder = GeometricSolverBuilder().with_deductive_agent(BFSDD())

    @pytest.mark.slow
    def test_imo_2000_p1_should_succeed(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b = segment a b; "
            "g1 = on_tline g1 a a b; "
            "g2 = on_tline g2 b b a; "
            "m = on_circle m g1 a, on_circle m g2 b; "
            "n = on_circle n g1 a, on_circle n g2 b; "
            "c = on_pline c m a b, on_circle c g1 a; "
            "d = on_pline d m a b, on_circle d g2 b; "
            "e = on_line e a c, on_line e b d; "
            "p = on_line p a n, on_line p c d; "
            "q = on_line q b n, on_line q c d "
            "? cong e p e q"
        ).build()

        success = solver.run()
        check.is_true(success)

    def test_incenter_excenter_should_fail(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = incenter d a b c; "
            "e = excenter e a b c "
            "? perp d c c e"
        ).build()
        success = solver.run(timeout=1)
        check.is_false(success)
        check.is_false(solver.run_infos["timeout"])
        check.is_false(solver.run_infos["overstep"])


class TestDDAR:
    @pytest.fixture(autouse=True)
    def setUpClass(self):
        self.solver_builder = GeometricSolverBuilder().with_deductive_agent(BFSDDAR())

    def test_incenter_excenter_should_succeed(self):
        # Note that this same problem should fail with DD only
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = incenter d a b c; "
            "e = excenter e a b c "
            "? perp d c c e"
        ).build()
        success = solver.run()
        check.is_true(success)

    def test_orthocenter_should_fail(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b "
            "? perp a d b c"
        ).build()
        success = solver.run()
        check.is_false(success)

    def test_orthocenter_aux_should_succeed(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b; "
            "e = on_line e a c, on_line e b d "
            "? perp a d b c"
        ).build()
        success = solver.run()
        check.is_true(success)

    def test_orthocenter_should_succeed_after_reset(self):
        """The solver should be reset (deductive agent and proof state)
        before adding auxiliary construction or attempting a new round of DDAR"""
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b "
            "? perp a d b c"
        ).build()
        success = solver.run()
        check.is_false(success)
        solver.add_auxiliary_construction("e = on_line e a c, on_line e b d")
        success = solver.run()
        check.is_true(success)
