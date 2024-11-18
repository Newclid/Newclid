from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Optional
import pytest

from newclid.agent.human_agent import HumanAgent
from newclid.api import GeometricSolverBuilder
from tests.fixtures import build_until_works

if TYPE_CHECKING:
    from newclid.proof import Proof


class HumanAgentWithPredefinedInput(HumanAgent):
    def __init__(
        self,
        inputs_given: Optional[list[str]] = None,
        show_figure: bool = False,
    ) -> None:
        super().__init__()
        self.inputs_given = inputs_given if inputs_given is not None else []
        self._n_figure_shown = 0
        self.show_figure = show_figure

    def _show_figure(self, proof: "Proof"):
        self._n_figure_shown += 1
        print("Showing figure")
        if self.show_figure:
            super()._show_figure(proof, block=True)

    def _ask_input(self, input_txt: str) -> str:
        next_input = self.inputs_given.pop(0)
        if isinstance(next_input, Callable):
            next_input = next_input(self)
        print(input_txt + next_input)
        return next_input


def pop_last_mapping(human_agent: HumanAgentWithPredefinedInput):
    if not human_agent._mappings:
        raise ValueError("No more mappings to pop. Actions were probably invalid.")
    return list(human_agent._mappings.keys())[-1]


class TestHumanAgent:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.human_agent = HumanAgentWithPredefinedInput()
        self.solver_builder = (
            GeometricSolverBuilder()
            .load_problem_from_txt(
                "a b c = triangle a b c; "
                "d = on_tline d b a c, on_tline d c a b "
                "? perp a d b c",
                translate=False,
            )
            .with_deductive_agent(self.human_agent)
        )

    def test_should_stop(self):
        self.human_agent.inputs_given = ["stop"]
        solver = self.solver_builder.build()
        success = solver.run()
        assert not success
        assert not solver.run_infos["timeout"]
        assert not solver.run_infos["overstep"]
        assert solver.run_infos["step"] == 1

    def test_should_match_and_apply_theorem(self):
        self.human_agent.inputs_given = [
            "match",
            "r21",
            "apply",
            "r21 a d c b",
            "stop",
        ]
        solver = self.solver_builder.load_problem_from_txt(
            "b = free b; "
            "c = free c; "
            "d = free d; "
            "a = on_circum a b c d, on_pline a d b c "
            "? eqangle b a d a d a d c",
            translate=False,
        ).build()
        success = solver.run()
        assert success

    def test_should_resolve_and_apply_derivation(self):
        self.human_agent.inputs_given = [
            "resolve",
            "ar",
            "import",
            "aconst b x a y 1pi/2",
            "stop",
        ]

        solver = build_until_works(
            self.solver_builder.load_problem_from_txt(
                "a b = segment a b; "
                "x = s_angle a b x 63o; "
                "y = s_angle b a y 153o "
                "? perp b x a y",
                translate=False,
            )
        )
        success = solver.run()
        assert success

    def test_should_solve_orthocenter_aux(self):
        self.human_agent.inputs_given = [
            "match",
            "r30",
            "apply",
            pop_last_mapping,
            "match",
            "r08",
            "apply",
            pop_last_mapping,
            "apply",
            pop_last_mapping,
            "match",
            "r34",
            "apply",
            pop_last_mapping,
            "match",
            "r39",
            "apply",
            pop_last_mapping,
            "stop",
        ]

        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b; "
            "e = on_line e a c, on_line e b d "
            "? perp a d b c",
            translate=False,
        ).build()
        success = solver.run()
        assert success

    def test_should_solve_orthocenter(self):
        self.human_agent.show_figure = False
        self.human_agent.inputs_given = [
            "show",
            "match",
            "r30",
            "apply",
            pop_last_mapping,
            "aux",
            "e = on_line e a c, on_line e b d",
            "show",
            "match",
            "r08",
            "apply",
            pop_last_mapping,
            "apply",
            pop_last_mapping,
            "match",
            "r34",
            "apply",
            pop_last_mapping,
            "show",
            "match",
            "r39",
            "apply",
            pop_last_mapping,
            "show",
            "stop",
        ]

        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b "
            "? perp a d b c",
            translate=False,
        ).build()
        success = solver.run()
        assert success

    def test_impossible_aux_feedback(self):
        self.human_agent.inputs_given = [
            "aux",
            "e = on_circle e n a, on_line e b c",
            "stop",
        ]
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = ieq_triangle a b c; m = midpoint m a b; n = midpoint n m a",
            translate=False,
        ).build()
        success = solver.run()
        assert not success
