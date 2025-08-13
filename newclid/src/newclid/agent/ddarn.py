"""Classical Breadth-First Search based agents."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from newclid.agent.agents_interface import DeductiveAgent
from newclid.predicates._index import PredicateType

if TYPE_CHECKING:
    from newclid.justifications.justification import Justification
    from newclid.proof_state import ProofState
    from newclid.rule import Rule

LOGGER = logging.getLogger(__name__)


class DDARNStats(BaseModel):
    """Statistics for the DDARN agent."""

    agent_type: Literal["ddarn"] = "ddarn"

    max_level: int
    """The maximum reached level of the DDARN agent."""

    level_predicate_count: list[tuple[int, PredicateType, int]]
    """How many predicates of each type do we have at each DDARN level of the diagram."""


class DDARN(DeductiveAgent):
    """Apply Deductive Derivation to exhaustion by Breadth-First Search.

    DDARN will match and apply all available rules level by level
    until reaching a fixpoint we call exhaustion.

    """

    def __init__(self) -> None:
        self.rule_buffer: list[Rule] = []
        self.exausted = False
        self.level = 0
        self.level_timer = time.time()
        self.proven_by_levels: dict[int, list[Justification]] = defaultdict(list)
        self.dd_cumulative_time = 0.0
        self.deductors_cumulative_time: dict[str, float] = defaultdict(lambda: 0.0)

    def get_stats(self) -> DDARNStats:
        return DDARNStats(
            max_level=self.level,
            level_predicate_count=_predicates_by_level(self.proven_by_levels),
        )

    def step(self, proof: ProofState, rules: list[Rule]) -> bool:
        if proof.check_goals():
            return False
        if self.rule_buffer:
            next_rule = self.rule_buffer.pop(0)
            self._match_and_apply_rule(next_rule, proof=proof)
        else:
            self._wrap_up_level(proof)
            if self.exausted:
                return False
            self._new_level(rules)
        return True

    def _match_and_apply_rule(self, rule: Rule, proof: ProofState) -> None:
        for dep in proof.match_theorem(rule):
            self._apply_dep(proof, dep)

    def _get_and_apply_from_deductors(self, proof: ProofState) -> dict[str, float]:
        time_per_deductor: dict[str, float] = {}
        for deductor in proof.deductors:
            t0 = time.time()
            for dep in deductor.deduce(proof.symbols):
                self._apply_dep(proof, dep)
            deductor_time = time.time() - t0
            time_per_deductor[deductor.__class__.__name__] = deductor_time
            self.deductors_cumulative_time[deductor.__class__.__name__] += deductor_time
        return time_per_deductor

    def _apply_dep(self, proof: ProofState, dep: Justification) -> None:
        if proof.apply(dep):
            self.proven_by_levels[self.level].append(dep)
            self.exausted = False

    def _wrap_up_level(self, proof: ProofState) -> None:
        dd_level_time = time.time() - self.level_timer
        deductors_t0 = time.time()
        time_per_deductor = self._get_and_apply_from_deductors(proof=proof)
        deductors_time = time.time() - deductors_t0
        times_str = ", ".join(
            f"{deductor_name}: {time:.2f}s"
            for deductor_name, time in time_per_deductor.items()
        )
        LOGGER.info(
            f"Level {self.level} completed in {dd_level_time + deductors_time:.2f}s"
            f" (DD: {dd_level_time:.2f}s, {times_str})"
        )
        self.dd_cumulative_time += dd_level_time

    def _new_level(self, rules: list[Rule]) -> None:
        self.exausted = True
        self.rule_buffer = list(rules)
        self.level += 1
        self.level_timer = time.time()


def _predicates_by_level(
    deps_by_level: dict[int, list[Justification]],
) -> list[tuple[int, PredicateType, int]]:
    histogram: list[tuple[int, PredicateType, int]] = []
    for level, deps in deps_by_level.items():
        level_histogram: dict[PredicateType, int] = {}
        for dep in deps:
            predicate_type = dep.predicate.predicate_type
            if predicate_type not in level_histogram:
                level_histogram[predicate_type] = 0
            level_histogram[predicate_type] += 1
        histogram.extend(
            [(level, pred, count) for pred, count in level_histogram.items()]
        )
    return histogram
