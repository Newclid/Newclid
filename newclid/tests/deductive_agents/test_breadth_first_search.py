import numpy as np
import pytest
from newclid.api import GeometricSolverBuilder, PythonDefault
from newclid.deductors.sympy_ar.algebraic_manipulator import SympyARDeductor
from newclid.jgex.problem_builder import JGEXProblemBuilder


class TestDDAR:
    @pytest.fixture(autouse=True)
    def setUpClass(self):
        self.rng = np.random.default_rng(998244353)
        self.solver_builder = GeometricSolverBuilder(
            rng=self.rng, api_default=PythonDefault(use_sympy_ar=True)
        )
        self.problem_builder = JGEXProblemBuilder(rng=self.rng)

    def test_incenter_excenter_should_succeed(self):
        problem_setup = self.problem_builder.with_problem_from_txt(
            "a b c = triangle a b c; d = incenter d a b c; e = excenter e a b c ? perp d c c e"
        ).build()
        solver = (
            self.solver_builder.with_deductors([SympyARDeductor()])
            .with_rules([])
            .build(problem_setup)
        )
        success = solver.run()
        assert success

    def test_orthocenter_should_succeed(self):
        problem_setup = self.problem_builder.with_problem_from_txt(
            "a b c = triangle a b c; d = on_tline d b a c, on_tline d c a b ? perp a d b c"
        ).build()
        solver = self.solver_builder.with_deductors([SympyARDeductor()]).build(
            problem_setup
        )
        success = solver.run()
        assert success
        # solver.write_proof_steps(Path(r"./tests_output/orthocenter_proof.txt"))
