"""Module containing the facade for the external API that must be maintained."""
# !!! Do not change the external API except if you know what you are doing !!!

from __future__ import annotations
import logging
from pathlib import Path
import traceback
from typing import TYPE_CHECKING, Optional, Type
from typing_extensions import Self
import copy as cp


from newclid.defs.clause import Clause
from newclid.defs.definition import Definition
from newclid.reasoning_engines import AlgebraicManipulator
from newclid.reasoning_engines.engines_interface import ReasoningEngine
from newclid.theorem import Theorem
from newclid.proof import Proof
from newclid.configs import default_defs_path, default_rules_path
from newclid.agent.breadth_first_search import BFSDDAR
from newclid.agent.agents_interface import AuxAction, DeductiveAgent
from newclid.run_loop import run_loop
from newclid.problem import Problem, setup_str_from_problem
from newclid.proof_writing import write_solution
from newclid.statements.adder import IntrinsicRules
from newclid._lazy_loading import lazy_import


if TYPE_CHECKING:
    import numpy

np: "numpy" = lazy_import("numpy")


class GeometricSolver:
    def __init__(
        self,
        proof_state: "Proof",
        problem: "Problem",
        defs: dict[str, "Definition"],
        rules: list["Theorem"],
        deductive_agent: Optional[DeductiveAgent] = None,
    ) -> None:
        self.proof_state = proof_state
        self.problem = problem
        self.defs = defs
        self.rules = rules
        self.problem_string = str(problem)
        if deductive_agent is None:
            deductive_agent = BFSDDAR()
        self.deductive_agent = deductive_agent
        self.run_infos = None
        # rng control
        self.rnd_gen = proof_state.get_rnd_generator()

    def load_state(self, proof_state: "Proof"):
        del self.proof_state
        self.proof_state = proof_state

    def load_problem_string(self, problem_string: str):
        self.problem_string = problem_string

    def get_problem_string(self) -> str:
        return self.problem_string

    def get_proof_state(self) -> str:
        return cp.deepcopy(self.proof_state)

    def get_defs(self):
        return self.defs

    def get_setup_string(self) -> str:
        return setup_str_from_problem(self.problem, self.defs)

    def update_random_generator(self, seed: int = 42):
        self.rnd_gen = np.random.default_rng(seed)
        return self.rnd_gen

    def run(
        self,
        max_steps: int = 10000,
        timeout: float = 600.0,
        stop_on_goal: bool = True,
        seed: Optional[int] = None,
    ) -> bool:
        self._reset(seed)
        success, infos = run_loop(
            self.deductive_agent,
            self.proof_state,
            self.rules,
            max_steps=max_steps,
            stop_on_goal=stop_on_goal,
            timeout=timeout,
        )
        self.run_infos = infos
        return success

    def write_solution(self, out_file: Path):
        write_solution(self.proof_state, self.problem, out_file)

    def draw_figure(self, out_file: Path):
        self.proof_state.symbols_graph.draw_figure(out_file)

    def draw_symbols_graph(self, out_file: Path):
        self.proof_state.symbols_graph.draw_html(out_file)

    def draw_why_graph(self, out_file: Path):
        self.proof_state.statements.graph.show_html(out_file)

    def write_all_outputs(self, output_folder_path: Path):
        output_folder_path.mkdir(exist_ok=True, parents=True)
        self.write_solution(output_folder_path / "proof_steps.txt")
        self.draw_figure(output_folder_path / "proof_figure.png")
        self.draw_symbols_graph(output_folder_path / "symbols_graph.html")
        logging.info("Written all outputs at %s", output_folder_path)

    def get_existing_points(self) -> list[str]:
        return [p.name for p in self.proof_state.symbols_graph.all_points()]

    def validate_clause_txt(self, clause_txt: str):
        if clause_txt.startswith("ERROR"):
            return clause_txt
        clause = Clause.from_txt(clause_txt)
        try:
            self.proof_state.copy().add_clause(
                clause, self.proof_state._plevel, self.defs
            )
        except Exception:
            return "ERROR: " + traceback.format_exc()
        return clause_txt

    def add_auxiliary_construction(self, aux_string: str):
        """Update the constructive statement of the problem with the aux point."""
        feedback = self.proof_state.step(AuxAction(aux_string))
        if not feedback.success:
            raise ValueError(f"Auxiliary construction failed to be added: {aux_string}")

    def _reset(self, seed: int):
        self.deductive_agent.reset()
        proof_state = self.get_proof_state()
        self.load_state(proof_state)

        self._reset_rnd_generator(seed)

        problem_string = self.get_problem_string()
        self.load_problem_string(problem_string)

    def _reset_rnd_generator(self, seed: int):
        rnd_gen = np.random.default_rng(seed)
        self.proof_state.set_rnd_generator(rnd_gen)
        self.rnd_gen = self.proof_state.get_rnd_generator()


class GeometricSolverBuilder:
    def __init__(self, seed: Optional[int] = None, no_goal: bool = False) -> None:
        self.problem: Optional[Problem] = None
        self.defs: Optional[list[Definition]] = None
        self.rules: Optional[list[Theorem]] = None
        self.deductive_agent: Optional[DeductiveAgent] = None
        self.disabled_intrinsic_rules: Optional[list[IntrinsicRules]] = None
        self.additional_reasoning_engine: dict[str, Type[ReasoningEngine]] = {
            "AR": AlgebraicManipulator
        }
        self.seed = seed
        self.no_goal = no_goal

    def build(self) -> "GeometricSolver":
        if self.problem is None:
            raise ValueError("Did not load problem before building solver.")

        if self.defs is None:
            self.defs = Definition.to_dict(
                Definition.from_txt_file(default_defs_path())
            )

        if self.rules is None:
            self.rules = Theorem.from_txt_file(default_rules_path())

        rnd_gen = np.random.default_rng(self.seed)

        if self.no_goal:
            self.problem.goals = []

        proof_state = Proof.build_problem(
            problem=self.problem,
            definitions=self.defs,
            disabled_intrinsic_rules=self.disabled_intrinsic_rules,
            additional_reasoning_engine=self.additional_reasoning_engine,
            rnd_generator=rnd_gen,
        )

        return GeometricSolver(
            proof_state,
            self.problem,
            self.defs,
            self.rules,
            self.deductive_agent,
        )

    def load_problem_from_file(
        self, problems_path: Path, problem_name: str, translate: bool = True
    ) -> Self:
        """
        `tranlate = True` by default for better LLM training
        """
        problems = Problem.to_dict(
            Problem.from_txt_file(problems_path, translate=translate)
        )
        if problem_name not in problems:
            raise ValueError(
                f"Problem name `{problem_name}` not found in {list(problems.keys())}"
            )
        self.problem = problems[problem_name]
        return self

    def load_problem_from_txt(
        self, problem_string: str, translate: bool = True
    ) -> Self:
        self.problem = Problem.from_txt(problem_string, translate)
        return self

    def load_rules_from_file(self, rules_path: Optional[Path] = None) -> Self:
        if rules_path is None:
            rules_path = default_rules_path()
        self.rules = Theorem.from_txt_file(rules_path)
        return self

    def load_defs_from_file(self, defs_path: Optional[Path] = None) -> Self:
        if defs_path is None:
            defs_path = default_defs_path()
        self.defs = Definition.to_dict(Definition.from_txt_file(defs_path))
        return self

    def load_defs_from_txt(self, defs_txt: str) -> Self:
        self.defs = Definition.to_dict(Definition.from_string(defs_txt))
        return self

    def with_deductive_agent(self, deductive_agent: DeductiveAgent) -> Self:
        self.deductive_agent = deductive_agent
        return self

    def with_disabled_intrinsic_rules(
        self, disabled_intrinsic_rules: list[IntrinsicRules]
    ) -> Self:
        self.disabled_intrinsic_rules = disabled_intrinsic_rules
        return self

    def with_additional_reasoning_engine(
        self, reasoning_engine: Type[ReasoningEngine], engine_name: str
    ) -> Self:
        self.additional_reasoning_engine[engine_name] = reasoning_engine
        return self
