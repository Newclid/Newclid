from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Optional
from typing_extensions import Self


from newclid.agent.ddarn import DDARN
from newclid.formulations.definition import DefinitionJGEX
from newclid.dependencies.dependency_graph import DependencyGraph
from newclid.load_geogebra import load_geogebra
from newclid.numerical.draw_figure import draw_figure
from newclid.algebraic_reasoning.algebraic_manipulator import (
    AlgebraicManipulator,
)
from newclid.formulations.rule import Rule
from newclid.proof import ProofState
from newclid.configs import default_defs_path, default_rules_path
from newclid.agent.agents_interface import DeductiveAgent
from newclid.run_loop import run_loop
from newclid.formulations.problem import ProblemJGEX
from newclid.proof_writing import write_proof_steps
import numpy as np

from newclid.statement import Statement
from newclid.tools import atomize
from newclid.webapp import pull_to_server

LOGGER = logging.getLogger(__name__)


class GeometricSolver:
    def __init__(
        self, proof: "ProofState", rules: list[Rule], deductive_agent: DeductiveAgent
    ) -> None:
        self.proof = proof
        self.rules = rules
        self.goals = proof.goals
        self.rng = proof.rng
        self.deductive_agent = deductive_agent
        self.run_infos: dict[str, Any] = {}

    def run(self) -> bool:
        infos = run_loop(self.deductive_agent, proof=self.proof, rules=self.rules)
        self.run_infos = infos
        return infos["success"]

    def write_proof_steps(self, out_file: Optional[Path] = None):
        write_proof_steps(self.proof, out_file)

    def draw_figure(self, *, out_file: Optional[Path] = None):
        draw_figure(self.proof, save_to=out_file, rng=self.rng)

    def write_run_infos(self, out_file: Optional[Path] = None):
        if out_file is None:
            print(self.run_infos)
        else:
            with open(out_file, "w", encoding="utf-8") as f:
                print(self.run_infos, file=f)

    def write_all_outputs(self, out_folder_path: Optional[Path] = None):
        out_folder_path = out_folder_path or self.proof.problem_path
        assert out_folder_path
        out_folder_path.mkdir(exist_ok=True, parents=True)
        self.write_run_infos(out_folder_path / "run_infos.txt")
        self.write_proof_steps(out_folder_path / "proof_steps.txt")
        self.draw_figure(out_file=out_folder_path / "proof_figure.svg")
        pull_to_server(self.proof, server_path=out_folder_path / "html")
        LOGGER.info("Written all outputs at %s", out_folder_path)


class GeometricSolverBuilder:
    def __init__(self, seed: Optional[int] = None) -> None:
        self.problemJGEX: Optional[ProblemJGEX] = None
        self._defs: Optional[dict[str, DefinitionJGEX]] = None
        self._rules: Optional[list[Rule]] = None
        self.goals: list[Statement] = []
        self.dep_graph = DependencyGraph(AlgebraicManipulator())
        self.deductive_agent: Optional[DeductiveAgent] = None
        self.seed = seed or 998244353
        self.problem_path: Optional[Path] = None
        self.draw_figure: bool = True

    @property
    def defs(self) -> dict[str, DefinitionJGEX]:
        if self._defs is None:
            self._defs = DefinitionJGEX.to_dict(
                DefinitionJGEX.parse_txt_file(default_defs_path())
            )
        return self._defs

    @property
    def rules(self) -> list[Rule]:
        if self._rules is None:
            self._rules = Rule.parse_txt_file(default_rules_path())
        return self._rules

    def build(self, max_attempts: int = 10000) -> "GeometricSolver":
        if self.problemJGEX:
            LOGGER.info(f"Use problemJGEX {self.problemJGEX} to build the proof state")
            proof_state = ProofState.build_problemJGEX(
                problemJGEX=self.problemJGEX,
                defsJGEX=self.defs,
                problem_path=self.problem_path,
                rng=np.random.default_rng(self.seed),
                max_attempts=max_attempts,
                draw_figure=self.draw_figure,
            )
        else:
            LOGGER.info("Use dep_graph to build the proof state")
            proof_state = ProofState(
                rng=np.random.default_rng(self.seed),
                dep_graph=self.dep_graph,
                problem_path=self.problem_path,
                goals=self.goals,
                defs=self.defs,
                draw_figure=self.draw_figure,
            )
        if self.deductive_agent is None:
            self.deductive_agent = DDARN()

        return GeometricSolver(proof_state, self.rules, self.deductive_agent)

    def load_problem_from_file(
        self, problems_path: Path, problem_name: str, rename: bool = False
    ) -> Self:
        """
        `translate = True` for better LLM training
        """
        self.problemJGEX = ProblemJGEX.from_file(problems_path, problem_name)
        if rename:
            self.problemJGEX = self.problemJGEX.renamed()
        return self

    def load_problem(self, problem: ProblemJGEX) -> Self:
        self.problemJGEX = problem
        return self

    def del_goals(self) -> Self:
        if self.problemJGEX:
            self.problemJGEX = ProblemJGEX(
                self.problemJGEX.name, self.problemJGEX.constructions, ()
            )
        self.goals = []
        return self

    def load_problem_from_txt(self, problem_txt: str) -> Self:
        self.problemJGEX = ProblemJGEX.from_text(problem_txt)
        return self

    def load_rules_from_txt(self, rule_txt: str) -> Self:
        self._rules = Rule.parse_text(rule_txt)
        return self

    def load_rules_from_file(self, rules_path: Optional[Path] = None) -> Self:
        if rules_path is None:
            rules_path = default_rules_path()
        self._rules = Rule.parse_txt_file(rules_path)
        return self

    def load_defs_from_file(self, defs_path: Optional[Path] = None) -> Self:
        if defs_path is None:
            defs_path = default_defs_path()
        self._defs = DefinitionJGEX.to_dict(DefinitionJGEX.parse_txt_file(defs_path))
        return self

    def load_defs_from_txt(self, defs_txt: str) -> Self:
        self._defs = DefinitionJGEX.to_dict(DefinitionJGEX.parse_text(defs_txt))
        return self

    def with_deductive_agent(self, deductive_agent: DeductiveAgent) -> Self:
        self.deductive_agent = deductive_agent
        return self

    def load_geogebra(self, path: Path) -> Self:
        load_geogebra(path, self.dep_graph)
        return self

    def load_goal(self, goal: str) -> Self:
        goal_statement = Statement.from_tokens(atomize(goal), self.dep_graph)
        assert goal_statement, "goal must parse"
        self.goals.append(goal_statement)
        return self

    def load_goals_file(self, path: Path) -> Self:
        for goal in atomize(path.read_text(), "\n"):
            if goal:
                self.load_goal(goal)
        return self

    def with_problem_path(self, path: Path) -> Self:
        self.problem_path = path
        return self

    def without_figure(self) -> Self:
        self.draw_figure = False
        return self
