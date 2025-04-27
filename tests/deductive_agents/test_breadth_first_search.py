import pytest

from newclid.agent.ddarn import DDARN
from newclid.api import GeometricSolverBuilder
from newclid.predicates.equal_angles import EqAngle
from newclid.statement import Statement


class TestDDAR:
    @pytest.fixture(autouse=True)
    def setUpClass(self):
        self.solver_builder = GeometricSolverBuilder(
            seed=998244353
        ).with_deductive_agent(DDARN())

    def test_incenter_excenter_should_succeed(self):
        solver = (
            self.solver_builder.load_problem_from_txt(
                "a b c = triangle a b c; "
                "d = incenter d a b c; "
                "e = excenter e a b c "
                "? perp d c c e"
            )
            .load_rules_from_txt("")
            .build()
        )
        success = solver.run()
        assert success

    def test_orthocenter_should_exhaust(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b "
            "? perp a d b c"
        ).build()
        success = solver.run()
        assert not success

    def test_orthocenter_aux_should_succeed(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b; "
            "e = on_line e a c, on_line e b d "
            "? perp a d b c"
        ).build()
        assert Statement.from_tokens(
            (EqAngle.NAME, "e", "a", "a", "b", "e", "b", "d", "c"),
            solver.proof.dep_graph,
        ).check()  # type: ignore
        assert Statement.from_tokens(
            (EqAngle.NAME, "e", "a", "a", "b", "e", "d", "d", "c"),
            solver.proof.dep_graph,
        ).check()  # type: ignore
        assert Statement.from_tokens(
            (EqAngle.NAME, "b", "e", "e", "a", "c", "e", "e", "d"),
            solver.proof.dep_graph,
        ).check()  # type: ignore
        success = solver.run()
        assert success
        # solver.write_proof_steps(Path(r"./tests_output/orthocenter_proof.txt"))
