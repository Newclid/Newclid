"""Classical Breadth-First Search based agents."""

from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Any, Callable, NamedTuple, Optional

from newclid.agent.agents_interface import DeductiveAgent
from newclid.agent.ddarn import DDARN
from newclid.justifications.justification import justify_dependency
from newclid.predicate_types import PredicateArgument
from newclid.predicates import predicate_from_construction
from newclid.problem import PredicateConstruction
from newclid.proof_state import ProofState
from newclid.rule import Rule
from newclid.tools import atomize


class NamedFunction(NamedTuple):
    name: str
    function: Callable[..., Any]


class HumanAgent(DeductiveAgent):
    def __init__(self) -> None:
        self.ddarn: Optional[DDARN] = None
        self.server: Optional[Path] = None

    @classmethod
    def select(
        cls,
        options: list[NamedFunction],
        allow_all: bool = False,
        allow_none: bool = False,
    ) -> NamedFunction | None:
        options_string = "\nSelect an option:"
        for i, option in enumerate(options):
            options_string += f"\n- [{i}] {option.name}"
        if allow_all:
            options_string += "- [all]"
        if allow_none:
            options_string += "- [none]"

        options_string += "\nChoose:"
        choice = input(options_string)
        if choice == "all":
            for option in options:
                option.function()
            return None
        if choice == "none":
            return None
        n = int(choice)
        return options[n]

    def step(self, proof: ProofState, rules: list[Rule]) -> bool:
        exausted = False
        match_rules = [
            NamedFunction(
                f"match {theorem.fullname}: {theorem}",
                self._fn_match(proof, theorem),
            )
            for theorem in rules
        ]
        if self.ddarn:
            if not self.ddarn.step(proof=proof, rules=rules):
                self.ddarn = None
        else:
            print("Premises:")
            for dep in proof.graph.premises():
                print(f"{dep.predicate}")
            selected = self.select(
                [
                    NamedFunction(
                        "match", partial(self.match, match_rules=match_rules)
                    ),
                    NamedFunction(
                        "update server", partial(self.update_server, proof=proof)
                    ),
                    NamedFunction(
                        "construction", partial(self.add_construction, proof=proof)
                    ),
                    NamedFunction("exhaust with ddarn", self.exhaust_with_ddarn),
                    NamedFunction("check predicate", partial(self.check, proof=proof)),
                    NamedFunction(
                        "check goals", partial(self.check_goals, proof=proof)
                    ),
                    NamedFunction("stop", lambda: None),
                ],
                allow_none=True,
            )
            if selected is None:
                return not exausted
            selected.function()
            if selected.name == "stop":
                exausted = True
        if proof.check_goals():
            print("All the goals are proven")
        else:
            for goal in proof.goals:
                print(f"{goal} proven? {proof.check(goal)}")
        return not exausted

    def match(self, match_rules: list[NamedFunction]) -> None:
        selected = self.select(match_rules, allow_none=True)
        if selected is not None:
            selected.function()

    def update_server(self, proof: "ProofState") -> None:
        self._pull_to_server(proof)

    def add_construction(self, proof: "ProofState") -> None:
        raise NotImplementedError

    def exhaust_with_ddarn(self) -> None:
        self.ddarn = DDARN()

    def check(self, proof: "ProofState") -> None:
        user_input: tuple[str, *tuple[PredicateArgument, ...]] = atomize(
            input("Check: ")
        )  # type: ignore
        predicate_construction = PredicateConstruction.from_tuple(user_input)
        predicate = predicate_from_construction(
            predicate_construction, proof.symbols.points
        )
        if predicate is None:
            print("predicate not parsed")
        else:
            print(f"Check result of {predicate}: {proof.check(predicate)}")

    def check_goals(self, proof: "ProofState") -> None:
        selects: list[NamedFunction] = [
            NamedFunction(
                f"check {goal}",
                lambda: print(f"Check result of {goal}: {proof.check(goal)}"),
            )
            for goal in proof.goals
        ]
        selected = self.select(selects, allow_all=True, allow_none=True)
        if selected is not None:
            selected.function()

    def _pull_to_server(self, proof: "ProofState"):  # type: ignore
        raise NotImplementedError
        # assert proof.problem_path
        # if not self.server:
        #     self.server = proof.problem_path / "html"
        #     run_static_server(self.server)
        # webapp.pull_to_server(proof, server_path=self.server)

    def _fn_match(self, proof: "ProofState", rule: Rule):
        def fn():
            deps = list(proof.match_theorem(rule))
            selected = self.select(
                [
                    NamedFunction(
                        f"{', '.join(str(s) for s in justify_dependency(dep, proof))} => {dep.predicate}",
                        lambda dep=dep: proof.apply(dep),
                    )
                    for dep in deps
                ],
                allow_all=True,
                allow_none=True,
            )
            if selected is None:
                return
            return selected.function

        return fn
