"""Classical Breadth-First Search based agents."""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Optional
import time

from newclid.agent.agents_interface import (
    ImportDerivationAction,
    ImportDerivationFeedback,
    ApplyTheoremFeedback,
    DeductiveAgent,
    Action,
    ResolveEngineAction,
    DeriveFeedback,
    Feedback,
    Mapping,
    MatchAction,
    MatchFeedback,
    ResetFeedback,
    StopAction,
    ApplyTheoremAction,
    StopFeedback,
)
from newclid.match_theorems import MatchCache
from newclid.predicates import Predicate
from newclid.reasoning_engines.engines_interface import Derivation


if TYPE_CHECKING:
    from newclid.theorem import Theorem
    from newclid.proof import Proof


class BFSDD(DeductiveAgent):
    """Apply Deductive Derivation to exaustion by Breadth-First Search.

    BFSDD will match and apply all available rules level by level
    until reaching a fixpoint we call exaustion.

    """

    def __init__(self) -> None:
        super().__init__()
        self.reset()

    def act(self, proof: "Proof", theorems: list["Theorem"]) -> Action:
        """Deduce new statements by applying
        breath-first search over all theorems one by one."""

        if self._unmatched_theorems:
            # We first match all unmatch theorems of the level
            return self._match_next_theorem(proof)

        if self._current_mappings or self._theorem_mappings:
            # Then we apply all gathered mappings of the level
            theorem, mapping = self._next_theorem_mapping()
            return ApplyTheoremAction(theorem, mapping)

        if self.level > 0 and not self._any_success_or_new_match_per_level[self.level]:
            # If one full level without new success we have saturated
            return StopAction()

        # Else we go to the next level
        self._next_level(theorems)
        if self._unmatched_theorems:
            return self._match_next_theorem(proof)
        return StopAction()

    def remember_effects(self, action: Action, feedback: Feedback):
        if isinstance(feedback, (StopFeedback, ResetFeedback)):
            return
        elif isinstance(feedback, ApplyTheoremFeedback):
            assert isinstance(action, ApplyTheoremAction)
            action_hash = _action_str(action.theorem, action.mapping)
            if feedback.success:
                self._any_success_or_new_match_per_level[self.level] = True
                self._actions_taken.add(action_hash)
                if action_hash in self._actions_failed:
                    self._actions_failed.remove(action_hash)
            else:
                self._actions_failed.add(action_hash)

        elif isinstance(feedback, MatchFeedback):
            new_mappings = self._filter_new_mappings(
                feedback.theorem, feedback.mappings
            )
            if len(new_mappings) > 0:
                self._theorem_mappings.append((feedback.theorem, new_mappings))
            for mapping in new_mappings:
                action_hash = _action_str(feedback.theorem, mapping)
                if action_hash not in self._actions_failed:
                    self._any_success_or_new_match_per_level[self.level] = True
        else:
            raise NotImplementedError()

    def _next_theorem_mapping(self) -> tuple[Optional["Theorem"], Optional[Mapping]]:
        if not self._current_mappings:
            new_mapping = self._theorem_mappings.pop(0)
            self._current_theorem, self._current_mappings = new_mapping
        return self._current_theorem, self._current_mappings.pop(0)

    def _filter_new_mappings(self, theorem: "Theorem", mappings: list[Mapping]):
        return [
            mapping
            for mapping in mappings
            if _action_str(theorem, mapping) not in self._actions_taken
        ]

    def _match_next_theorem(self, proof: "Proof"):
        if self._match_cache is None:
            self._match_cache = MatchCache(proof)
        next_theorem = self._unmatched_theorems.pop(0)
        return MatchAction(next_theorem, cache=self._match_cache)

    def _next_level(self, theorems: list["Theorem"]):
        self._update_level()
        self._any_success_or_new_match_per_level[self.level] = False
        if self._match_cache is not None:
            self._match_cache.reset()
        self._unmatched_theorems = theorems.copy()

    def _update_level(self):
        if self.level == 0:
            self.level = 1
            self._level_start_time = time.time()
            return

        logging.info(
            f"Level {self.level} exausted"
            f" | Time={ time.time() - self._level_start_time:.1f}s"
        )
        self._level_start_time = time.time()
        self.level += 1

    def reset(self):
        self.level = 0

        self._theorem_mappings: list[tuple["Theorem", list[Mapping]]] = []
        self._actions_taken: set[str] = set()
        self._actions_failed: set[str] = set()

        self._current_mappings: list[Mapping] = []
        self._current_theorem: Optional["Theorem"] = None
        self._level_start_time: float = time.time()

        self._unmatched_theorems: list["Theorem"] = []
        self._match_cache: Optional[MatchCache] = None
        self._any_success_or_new_match_per_level: dict[int, bool] = {}


def _action_str(theorem: "Theorem", mapping: Mapping) -> str:
    arg_names = [point.name for arg, point in mapping.items() if isinstance(arg, str)]
    return ".".join([theorem.name] + arg_names)


class BFSDDAR(DeductiveAgent):
    """The traditional engine of GeoSolver presented in the original AlphaGeometry.

    BFSDDAR is composed of two phases:

    1. BFSDD exhaustively runs all rules until exaustion. Each new BFSDD level,
       potential additional derivations will be collected from reasoning engines
       such as the AlgebraicManipulator (AR).
    2. Once BFSDD's fixpoint is reached, we import derivations from reasoning engines
       to get new predicates, and restart the DD loop.
       If no new predicate can be found, then BFSDDAR is exausted.

    """

    def __init__(
        self,
        do_simple_derivations_asap: bool = False,
        do_all_derivations_asap: bool = False,
    ) -> None:
        super().__init__()
        self._dd_agent = BFSDD()
        self._do_simple_derivations_asap = do_simple_derivations_asap
        self._do_all_derivations_asap = do_all_derivations_asap
        self.reset()

    def act(self, proof: "Proof", theorems: list["Theorem"]) -> Action:
        """Deduce new statements by applying
        breath-first search over all theorems one by one."""

        if self._do_simple_derivations_asap or self._do_all_derivations_asap:
            next_derivation = self._apply_next_derivation(
                include_eq4s=self._do_all_derivations_asap
            )
            if next_derivation is not None:
                return next_derivation

        if self._current_next_engines:
            # If we have a stack of engines to use, we do that first
            next_engine = self._current_next_engines.pop()
            return ResolveEngineAction(engine_id=next_engine)

        if self.level != self._dd_agent.level:
            # Each new level of dd we derive first
            self.level = self._dd_agent.level
            self._current_next_engines = self.available_engines.copy()
            next_engine = self._current_next_engines.pop()
            return ResolveEngineAction(engine_id=next_engine)

        dd_action = self._dd_agent.act(proof, theorems)
        if isinstance(dd_action, StopAction):
            # If dd is saturated we start derivating
            next_derivation = self._apply_next_derivation()
            if next_derivation is None:
                # If no more derivations, we have exausted AR too
                return StopAction()
            return next_derivation

        # Else we just use dd_action
        return dd_action

    def remember_effects(self, action: Action, feedback: Feedback):
        if isinstance(feedback, ResetFeedback):
            self.available_engines = feedback.available_engines
        if isinstance(feedback, DeriveFeedback):
            for derive in feedback.derivations:
                predicate = derive.statement.predicate
                if predicate == Predicate.EQANGLE or predicate == Predicate.EQRATIO:
                    self._eq4s.append(derive)
                else:
                    self._derivations.append(derive)
        elif isinstance(feedback, ImportDerivationFeedback):
            new_statements = len(feedback.added) > 1
            if new_statements:
                # dd is not saturated anymore
                self._dd_agent._any_success_or_new_match_per_level[self.level] = True
        else:
            self._dd_agent.remember_effects(action, feedback)

    def _apply_next_derivation(
        self, include_eq4s: bool = True
    ) -> Optional[ImportDerivationAction]:
        if not self._current_derivation_stack:
            if self._derivations:
                self._current_derivation_stack = self._derivations
                self._derivations = []
            elif include_eq4s and self._eq4s:
                self._current_derivation_stack = self._eq4s
                self._eq4s = []
            else:
                return None

        return ImportDerivationAction(derivation=self._current_derivation_stack.pop())

    def reset(self):
        self._dd_agent.reset()
        self._derivations: list[Derivation] = []
        self._eq4s: list[Derivation] = []
        self._current_derivation_stack: list[Derivation] = []
        self._current_next_engines: list[str] = []
        self.level: int = -1
