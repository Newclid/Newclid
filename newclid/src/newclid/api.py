"""External API for Newclid.

This module contains the main entry point for building and using a geometric solver.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.random import Generator as RngGenerator
from typing_extensions import Self

from newclid.agent.agents_interface import DeductiveAgent
from newclid.agent.ddarn import DDARN
from newclid.all_rules import DEFAULT_RULES
from newclid.animation import ProofAnimation
from newclid.api_defaults import APIDefault
from newclid.deductors.deductor_interface import Deductor
from newclid.deductors.sympy_ar.algebraic_manipulator import SympyARDeductor
from newclid.draw.figure import draw_figure
from newclid.draw.theme import DrawTheme
from newclid.jgex.formulation import JGEXFormulation
from newclid.predicates import Predicate
from newclid.problem import (
    PredicateConstruction,
    ProblemSetup,
    predicate_to_construction,
)
from newclid.proof_data import proof_data_from_state
from newclid.proof_state import ProofState
from newclid.proof_writing import write_proof
from newclid.rng import setup_rng
from newclid.rule import Rule, rules_from_file
from newclid.rule_matching.interface import RuleMatcher
from newclid.rule_matching.mapping_matcher import FilterMapper, MappingMatcher
from newclid.run_loop import RunInfos, run_loop
from newclid.webapp import pull_to_server

LOGGER = logging.getLogger(__name__)


class GeometricSolver:
    """External API for solving a geometric problem."""

    def __init__(
        self, proof: ProofState, rules: list[Rule], deductive_agent: DeductiveAgent
    ) -> None:
        self.proof_state = proof
        self.rules = rules
        self.rng = proof.rng
        self.deductive_agent = deductive_agent
        self.run_infos: RunInfos | None = None

    def run(self) -> bool:
        infos = run_loop(self.deductive_agent, proof=self.proof_state, rules=self.rules)
        self.run_infos = infos
        return infos.success

    def proof(
        self, goals_constructions: list[PredicateConstruction] | None = None
    ) -> str:
        if goals_constructions is None:
            goals_constructions = [
                predicate_to_construction(goal) for goal in self.proof_state.goals
            ]
        proof_data = proof_data_from_state(
            goals_constructions=goals_constructions, proof_state=self.proof_state
        )
        return write_proof(proof_data)

    def animate(
        self,
        jgex_problem: JGEXFormulation | None = None,
        theme: DrawTheme | None = None,
    ) -> FuncAnimation:
        goals_constructions = [
            predicate_to_construction(goal) for goal in self.proof_state.goals
        ]
        proof_data = proof_data_from_state(
            goals_constructions=goals_constructions, proof_state=self.proof_state
        )
        return ProofAnimation(
            proof_data=proof_data,
            symbols=self.proof_state.symbols,
            image_path=None,
            jgex_problem=jgex_problem,
            theme=theme if theme is not None else DrawTheme(),
        ).animate()

    def draw_figure(
        self,
        *,
        out_file: Optional[Path] = None,
        jgex_problem: JGEXFormulation | None,
        theme: DrawTheme | None = None,
    ) -> tuple[Figure, Axes]:
        fig, ax = plt.subplots()  # pyright: ignore
        return draw_figure(
            fig,
            ax,
            self.proof_state,
            jgex_problem=jgex_problem,
            theme=theme if theme is not None else DrawTheme(),
            save_to=out_file,
        )

    def write_all_outputs(
        self, out_folder_path: Path, jgex_problem: JGEXFormulation | None
    ):
        out_folder_path.mkdir(exist_ok=True, parents=True)
        with open(out_folder_path / "run_infos.json", "w", encoding="utf-8") as f:
            if self.run_infos is not None:
                f.write(self.run_infos.model_dump_json(indent=2))
            else:
                f.write("{}")
        with open(out_folder_path / "proof.txt", "w", encoding="utf-8") as f:
            f.write(self.proof())
        self.draw_figure(
            out_file=out_folder_path / "proof_figure.svg", jgex_problem=jgex_problem
        )
        pull_to_server(self.proof_state, server_path=out_folder_path / "html")
        LOGGER.info("Written all outputs at %s", out_folder_path)


class ProblemBuilder(ABC):
    """Interface for building a problem."""

    @abstractmethod
    def build(self) -> ProblemSetup:
        """Build a problem to be fed to the solver."""


class PythonDefault(APIDefault):
    def __init__(self, use_sympy_ar: bool = True) -> None:
        self.use_sympy_ar = use_sympy_ar

    def default_rule_matcher(self) -> RuleMatcher:
        return MappingMatcher(FilterMapper())

    def default_deductors(self) -> list[Deductor]:
        if self.use_sympy_ar:
            return [SympyARDeductor()]
        return []

    def default_deductive_agent(self) -> DeductiveAgent:
        return DDARN()

    def callback(self, proof_state: ProofState) -> None:
        pass


class GeometricSolverBuilder:
    """Main entry point for building a geometric solver.

    Adding or removing methods should be done with care as it represents the external API and should be stable.
    """

    def __init__(
        self,
        rng: RngGenerator | int | None = None,
        api_default: APIDefault | None = None,
    ) -> None:
        self.rng = setup_rng(rng)
        self.goals: list[Predicate] = []
        self.deductors: list[Deductor] | None = None
        self.deductive_agent: DeductiveAgent | None = None
        self.rule_matcher: Optional[RuleMatcher] = None
        self.rules: list[Rule] = sorted(DEFAULT_RULES, key=lambda r: r.id)
        self.api_default = (
            api_default if api_default is not None else _load_api_default()
        )

    def build(self, problem_setup: ProblemSetup) -> GeometricSolver:
        """Build a geometric solver with the current configuration on the given problem setup."""
        if (
            self.rule_matcher is None
            or self.deductors is None
            or self.deductive_agent is None
        ):
            if self.rule_matcher is None:
                self.rule_matcher = self.api_default.default_rule_matcher()
            if self.deductors is None:
                self.deductors = self.api_default.default_deductors()
            if self.deductive_agent is None:
                self.deductive_agent = self.api_default.default_deductive_agent()

        proof_state = ProofState(
            problem=problem_setup,
            rule_matcher=self.rule_matcher,
            deductors=self.deductors,
            rng=self.rng,
        )

        self.api_default.callback(proof_state)
        return GeometricSolver(proof_state, self.rules, self.deductive_agent)

    def with_deductive_agent(self, deductive_agent: DeductiveAgent) -> Self:
        self.deductive_agent = deductive_agent
        return self

    def with_rule_matcher(self, rule_matcher: RuleMatcher) -> Self:
        self.rule_matcher = rule_matcher
        return self

    def with_deductors(self, deductors: list[Deductor]) -> Self:
        self.deductors = deductors
        return self

    def with_rules(self, rules: list[Rule]) -> Self:
        self.rules = rules
        return self

    def with_rules_from_file(self, rules_path: Path) -> Self:
        self.with_rules(rules_from_file(rules_path))
        return self


def _load_api_default() -> APIDefault:
    try:
        from py_yuclid.api_default import HEDefault  # type: ignore

        return HEDefault()  # type: ignore
    except ImportError:
        return PythonDefault()  # type: ignore
