"""Human based agent.

This is a useful tool for analysis and understanding how GeoSolver behaves.

"""

from __future__ import annotations
from typing import NamedTuple, Optional, TypeVar

from newclid.reasoning_engines.engines_interface import Derivation
from newclid.statements.statement import Statement
from newclid.theorem import Theorem
from newclid.agent.agents_interface import (
    Action,
    ImportDerivationAction,
    ImportDerivationFeedback,
    ApplyTheoremAction,
    ApplyTheoremFeedback,
    AuxAction,
    AuxFeedback,
    DeductiveAgent,
    ResolveEngineAction,
    DeriveFeedback,
    Feedback,
    Mapping,
    MatchAction,
    MatchFeedback,
    ResetAction,
    ResetFeedback,
    StopAction,
    StopFeedback,
)
from newclid.predicates import Predicate
from newclid.dependencies.dependency import Dependency
from newclid.problem import Problem
from newclid.proof import Proof, theorem_mapping_str
from newclid.statements.adder import ToCache

from colorama import just_fix_windows_console
from colorama import Fore, Style

just_fix_windows_console()

T = TypeVar("T")


class ShowAction(NamedTuple):
    """Display the figure of the current proof state."""


class HumanAgent(DeductiveAgent):
    """Human decisions based agent.

    Allow the user to interact with the solver as a deductive agent would.

    """

    _INPUT_TO_ACTION_TYPE = {
        "show": ShowAction,
        "match": MatchAction,
        "apply": ApplyTheoremAction,
        "resolve": ResolveEngineAction,
        "import": ImportDerivationAction,
        "aux": AuxAction,
        "stop": StopAction,
    }
    _ACTION_TYPE_DESCRIPTION = {
        MatchAction: "Match a theorem to know on which mappings it can be applied.",
        StopAction: "Stop the proof",
        ApplyTheoremAction: "Apply a theorem on a mapping of points.",
        ResolveEngineAction: "Resolve available derivation from current proof state.",
        ImportDerivationAction: "Apply a derivation.",
        AuxAction: "Add an auxiliary construction to the setup.",
        ShowAction: "Show the geometric figure of the current proof.",
    }

    def __init__(self) -> None:
        super().__init__()
        self._problem: Optional[Problem] = None
        self.reset()

    def act(self, proof: Proof, theorems: list[Theorem]) -> Action:
        ACTION_TYPE_ACT = {
            StopAction: self._act_stop,
            MatchAction: self._act_match,
            ApplyTheoremAction: self._act_apply_theorem,
            ResolveEngineAction: self._act_resolve_derivations,
            ImportDerivationAction: self._act_apply_derivation,
            AuxAction: self._act_aux,
            ShowAction: self._act_show,
        }

        action = None
        while action is None:
            choosen_action_type = self._choose_action_type()
            act_method = ACTION_TYPE_ACT[choosen_action_type]
            action = act_method(theorems)
            if isinstance(action, ShowAction):
                action = self._show_figure(proof)

        if isinstance(action, (ApplyTheoremAction, ImportDerivationAction)):
            self.level += 1
        return action

    def reset(self):
        self._mappings: dict[str, tuple[Theorem, Mapping]] = {}
        self._known_mappings: set[str] = set()

        self._derivations: dict[str, Derivation] = {}
        self._known_derivations: set[Statement] = set()

        self._all_added: list[Statement] = []
        self._all_cached: list[Statement] = []

        self._known_engines: list[str] = []

        self.level = 0

    def _act_show(self, theorems: list[Theorem]):
        return ShowAction()

    def _act_stop(self, theorems: list[Theorem]) -> StopAction:
        return StopAction()

    def _act_match(self, theorems: list[Theorem]) -> MatchAction:
        choose_theorem_str = "\nChoose a theorem: \n"
        for th in theorems:
            choose_theorem_str += f" - [{th.rule_name}]: {th}\n"
        choose_theorem_str += (
            "Theorem you want to match (type only the name within brackets): "
        )
        theorem_dict = {th.rule_name: th for th in theorems}
        theorem = self._ask_for_key(theorem_dict, choose_theorem_str)
        return MatchAction(theorem)

    def _act_apply_theorem(self, theorems: list[Theorem]) -> ApplyTheoremAction:
        choosen_mapping_str = "\nAvailable theorems mappings: \n"
        for mapping_str in self._mappings.keys():
            choosen_mapping_str += f" - [{mapping_str}]\n"
        choosen_mapping_str += "Mapping you want to apply: "
        theorem, mapping = self._ask_for_key(
            self._mappings, choosen_mapping_str, pop=True
        )
        return ApplyTheoremAction(theorem, mapping)

    def _act_resolve_derivations(self, theorems: list[Theorem]) -> ResolveEngineAction:
        choice_str = "\nAvailable reasoning engines: \n"
        engines_to_choose = {
            engine_id.lower(): engine_id for engine_id in self._known_engines
        }
        for engine_id in engines_to_choose.keys():
            choice_str += f" - [{engine_id}]\n"

        choice_str += "Reasoning engine you want to resolve: "
        engine_id = self._ask_for_key(engines_to_choose, choice_str)

        return ResolveEngineAction(engine_id=engine_id)

    def _act_apply_derivation(self, theorems: list[Theorem]) -> ImportDerivationAction:
        choose_derivation_str = "\nAvailable derivations: \n"
        for derived_statement_str in self._derivations.keys():
            choose_derivation_str += f" - [{derived_statement_str}]\n"
        choose_derivation_str += "Derivation you want to apply: "
        derivation = self._ask_for_key(
            self._derivations, choose_derivation_str, pop=True
        )
        return ImportDerivationAction(derivation=derivation)

    def _act_aux(self, theorems: list[Theorem]) -> AuxAction:
        aux_string = self._ask_input("Auxiliary string: ")
        return AuxAction(aux_string)

    def remember_effects(self, action: Action, feedback: Feedback):
        feedback_type_to_method = {
            ResetFeedback: self._remember_reset,
            StopFeedback: self._remember_stop,
            MatchFeedback: self._remember_match,
            ApplyTheoremFeedback: self._remember_apply_theorem,
            DeriveFeedback: self._remember_derivations,
            ImportDerivationFeedback: self._remember_apply_derivation,
            AuxFeedback: self._remember_aux,
        }

        for feedback_type, feedback_process in feedback_type_to_method.items():
            if isinstance(feedback, feedback_type):
                additional_feedback = feedback_type != StopFeedback
                feedback_txt, success = feedback_process(action, feedback)
                self._display_feedback(
                    "\n" + feedback_txt,
                    additional_feedback=additional_feedback,
                    color=Fore.GREEN if success else Fore.RED,
                )
                return

        raise NotImplementedError(f"Feedback {type(feedback)} is not implemented.")

    def _remember_reset(
        self, action: ResetAction, feedback: ResetFeedback
    ) -> tuple[str, bool]:
        self._problem = feedback.problem
        self._known_engines = feedback.available_engines
        feedback_str = f"\nStarting problem {self._problem.url}:"
        feedback_str += "\n" + "=" * (len(feedback_str) - 2) + "\n"

        feedback_str += "\n  Initial statements:\n"
        if feedback.added:
            feedback_str += self._list_added_statements(feedback.added)
        if feedback.to_cache:
            feedback_str += self._list_cached_statements(feedback.to_cache)

        return feedback_str, True

    def _remember_stop(
        self, action: StopAction, feedback: StopFeedback
    ) -> tuple[str, bool]:
        if feedback.success:
            return "Congratulations ! You have solved the problem !\n", True
        return "You did not solve the problem.\n", False

    def _remember_match(
        self, action: MatchAction, feedback: MatchFeedback
    ) -> tuple[str, bool]:
        matched_theorem = feedback.theorem
        theorem_str = f"[{matched_theorem.rule_name}] ({matched_theorem})"
        if not feedback.mappings:
            return f"No match found for theorem {theorem_str}:\n", False

        feedback_str = f"Matched theorem {theorem_str}:\n"
        for mapping in feedback.mappings:
            mapping_str = theorem_mapping_str(matched_theorem, mapping)
            if mapping_str in self._known_mappings:
                continue
            self._mappings[mapping_str] = (matched_theorem, mapping)
            self._known_mappings.add(mapping_str)
            feedback_str += f"  - [{mapping_str}]\n"
        return feedback_str, True

    def _remember_apply_theorem(
        self, action: ApplyTheoremAction, feedback: ApplyTheoremFeedback
    ) -> tuple[str, bool]:
        theorem = action.theorem
        rname = theorem.rule_name
        if not feedback.success:
            return f"Failed to apply theorem [{rname}] ({theorem})\n", False

        feedback_str = f"Successfully applied theorem [{rname}] ({theorem}):\n"
        if feedback.added:
            feedback_str += self._list_added_statements(feedback.added)
        if feedback.to_cache:
            feedback_str += self._list_cached_statements(feedback.to_cache)
        if not feedback.added and not feedback.to_cache:
            feedback_str += "But no statements were added nor cached ...\n"
        return feedback_str, True

    def _remember_derivations(
        self, action: ResolveEngineAction, feedback: DeriveFeedback
    ) -> tuple[str, bool]:
        if not feedback.derivations:
            return "No new derivation found.\n", False

        feedback_str = "New derivations:\n"
        for derivation in feedback.derivations:
            if derivation.statement in self._known_derivations:
                continue
            self._derivations[str(derivation.statement)] = derivation
            self._known_derivations.add(derivation.statement)
            feedback_str += f"  - [{derivation.statement}]\n"
        return feedback_str, True

    def _remember_apply_derivation(
        self, action: ImportDerivationAction, feedback: ImportDerivationFeedback
    ) -> tuple[str, bool]:
        success = True
        feedback_str = (
            f"Successfully applied derivation [{action.derivation.statement}]:\n"
        )
        if feedback.added:
            feedback_str += self._list_added_statements(feedback.added)
        if feedback.to_cache:
            feedback_str += self._list_cached_statements(feedback.to_cache)
        if not feedback.added and not feedback.to_cache:
            feedback_str += "But no statements were added nor cached ...\n"
            success = False
        return feedback_str, success

    def _remember_aux(self, action: AuxAction, feedback: AuxFeedback):
        success = feedback.success

        aux_str = action.aux_string
        if not success:
            return (
                f"Failed to add auxiliary construction  [{aux_str}]\n"
                "Check that the format is correct "
                "and that the construction is possible.\n",
                False,
            )

        feedback_str = f"Successfully added auxiliary construction [{aux_str}]:\n"
        if feedback.added:
            feedback_str += self._list_added_statements(feedback.added)
        if feedback.to_cache:
            feedback_str += self._list_cached_statements(feedback.to_cache)
        if not feedback.added and not feedback.to_cache:
            feedback_str += "But no statements were added nor cached ...\n"
            success = False
        return feedback_str, success

    def _list_added_statements(self, added: list[Dependency]) -> str:
        feedback_str = "    Added statements:\n"
        for dep in added:
            feedback_str += f"    - {dep.statement}\n"
            self._all_added.append(dep.statement)
        return feedback_str

    def _list_cached_statements(self, to_cache: list[ToCache]) -> str:
        feedback_str = "    Cached statements:\n"
        for cached in to_cache:
            cached_statement, _deps = cached
            self._all_cached.append(cached_statement)
            feedback_str += f"    - {cached_statement}"
            if str(cached_statement) != str(_deps.statement):
                feedback_str += f" ({_deps.statement})"
            feedback_str += "\n"
        return feedback_str

    def _choose_action_type(self):
        availables_action_types = self._INPUT_TO_ACTION_TYPE.copy()
        for action_input, action_type in self._INPUT_TO_ACTION_TYPE.items():
            if action_type == ApplyTheoremAction and not self._mappings:
                availables_action_types.pop(action_input)
            if action_type == ImportDerivationAction and not self._derivations:
                availables_action_types.pop(action_input)

        choose_action_type_str = "\nChoose an action type:\n"
        for action_input, action_type in availables_action_types.items():
            action_description = self._ACTION_TYPE_DESCRIPTION[action_type]
            choose_action_type_str += f" -  [{action_input}]: {action_description}\n"
        choose_action_type_str += "Your choice: "
        return self._ask_for_key(availables_action_types, choose_action_type_str)

    def _ask_for_key(
        self,
        dict_to_ask: dict[str, T],
        input_txt: str,
        not_found_txt: str = "Invalid input, try again.\n",
        pop: int = False,
    ) -> T:
        choosen_value = None
        while choosen_value is None:
            if not dict_to_ask:
                raise ValueError("No value to ask for.")
            choosen_input = self._ask_input(input_txt)
            if pop:
                choosen = dict_to_ask.pop(choosen_input, None)
            else:
                choosen = dict_to_ask.get(choosen_input, None)
            if choosen is not None:
                choosen_value = choosen
            else:
                self._display_feedback(
                    not_found_txt, color=Fore.RED, additional_feedback=True
                )
        return choosen_value

    def _display_feedback(
        self,
        feedback: str,
        additional_feedback: bool = False,
        color: int = Fore.WHITE,
    ):
        if additional_feedback:
            print()
            if self._all_cached:
                print(_list_statements("All cached statements:\n", self._all_cached))
            if self._all_added:
                print(_list_statements("All added statements:\n", self._all_added))

        print(color + feedback + Style.RESET_ALL)
        print("-" * 50)

        if not additional_feedback or self._problem is None:
            return

        print(_pretty_problem(self._problem))

    def _ask_input(self, input_txt: str) -> str:
        return input(input_txt).lower().strip()

    def _show_figure(self, proof: "Proof", block: bool = False):
        equal_angles = {}
        for eqangle in self._all_cached:
            if eqangle.predicate != Predicate.EQANGLE:
                continue
            hashed_eqangle = eqangle.hash_tuple
            if hashed_eqangle not in equal_angles:
                equal_angles[hashed_eqangle] = eqangle.args
        proof.symbols_graph.draw_figure(
            equal_angles=list(equal_angles.values()), block=block
        )


def _pretty_problem(problem: "Problem"):
    problem_initial_txt = str(problem).replace("; ", "\n").split(" ? ")[0]
    return (
        Fore.BLUE
        + f"Problem:\n{problem_initial_txt}\n"
        + Style.RESET_ALL
        + "\n"
        + Fore.YELLOW
        + f"Current goals:\n{problem.goals}"
        + Style.RESET_ALL
    )


def _list_statements(
    heading: str, statements: list[Statement], indent: str = ""
) -> str:
    feedback_str = heading
    for statement in statements:
        feedback_str += indent + f"- {statement}\n"
    return feedback_str
