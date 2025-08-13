import io
import sys

import numpy as np
import pytest
from newclid.agent.human_agent import HumanAgent
from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder


class TestHumanAgent:
    @pytest.fixture(autouse=True)
    def setUpClass(self):
        self.rng = np.random.default_rng(998244353)
        self.problem_builder = JGEXProblemBuilder(rng=self.rng)
        self.solver_builder = GeometricSolverBuilder(rng=self.rng).with_deductive_agent(
            HumanAgent()
        )

    @pytest.mark.skip(reason="Annoying popup for unnecessary feature")
    def test_graphics(self):
        sys.stdin = io.StringIO("1\n5\nall\n6\n")
        self.problem_builder.with_problem_from_txt(
            "a b c = triangle a b c;h = on_tline h b a c, on_tline h c a b ? perp a h b c"
        )
        solver = self.solver_builder.with_rules([]).build(self.problem_builder)
        solver.run()

    @pytest.mark.skip(reason="Annoying popup for unnecessary feature")
    def test_add_construction(self):
        sys.stdin = io.StringIO("2\nd = on_line d a c, on_line d b h\n3\n6\n")
        self.problem_builder.with_problem_from_txt(
            "a b c = triangle a b c;h = on_tline h b a c, on_tline h c a b ? perp a h b c"
        )
        solver = self.solver_builder.with_rules([]).build(self.problem_builder)
        assert solver.run()
