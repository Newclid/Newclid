import logging

import numpy as np
import pytest
from newclid.agent.follow_deductions import FollowDeductions
from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.rule import Rule
from py_yuclid.api_default import HEDefault
from py_yuclid.yuclid_adapter import YuclidAdapter


class TestYuclidCustomRuleIntegration:
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

    def test_custom_rule_passed_via_temp_file(self):
        """
        Uses a problem (IMO 2012 P5) that the standard engine CANNOT solve natively.
        By injecting a custom cheat rule that bridges the assumptions to the goal,
        we guarantee the engine must use our rule to succeed.
        """

        custom_rule = Rule(
            id="custom_imo_cheat",
            description="Cheat rule: intersecting lines imply congruent segments",
            premises_txt=("coll X Y Z", "coll X W U"),
            conclusions_txt=("cong X U X Z",),
        )

        self.solver_builder.with_additional_rules([custom_rule])

        # 'a' as midpoint of 'b' and 'c' guarantees that AB = AC and they form a line.
        # This makes our custom rule numerically true!
        problem_txt = (
            "c a b = r_triangle c a b; d = foot d c a b; x = on_line x c d;"
            " k = on_line k a x, on_circle k b c; l = on_line l b x, on_circle l a c;"
            " m = on_line m a l, on_line m b k"
            " ? cong m k m l"
        )

        problem_setup = self.problem_builder.with_problem_from_txt(problem_txt).build()

        self.he_adapter.problem_name = "custom_rule_integration"
        solver = self.solver_builder.build(problem_setup)

        success = solver.run()

        # Ensure the engine reached the goal
        assert success, "The solver failed to reach the goal."

        # Verify it was the custom rule that was mapped back
        custom_rule_obj = next(
            r for r in self.solver_builder.rules if r.id == "custom_imo_cheat"
        )

        matches = self.he_adapter.rule_matches(custom_rule_obj, problem_setup)

        assert len(matches) > 0, "No matches were found for the custom rule."
        assert matches[0].rule.id == "custom_imo_cheat"

        deductions_used = self.he_adapter.ordered_deductions_for_problem(problem_setup)
        rule_ids_used = [deduction.rule.id for deduction in deductions_used]
        assert "custom_imo_cheat" in rule_ids_used, (
            "Rule hasn't been used in the proof."
        )
