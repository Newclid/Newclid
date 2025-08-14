"""Module to compute the justifications of the goals."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from newclid.justifications._index import JustificationError
from newclid.justifications.justification import justify_dependency

if TYPE_CHECKING:
    from newclid.justifications.justification import Justification
    from newclid.predicates import Predicate
    from newclid.proof_state import ProofState

LOGGER = logging.getLogger(__name__)


def goals_justifications(
    goals: list[Predicate], proof_state: ProofState
) -> tuple[tuple[Justification, ...], dict[Predicate, bool]]:
    sub_proof: dict[Predicate, tuple[Justification, ...]] = {}
    proof_steps: list[Justification] = []
    goal_is_proven: dict[Predicate, bool] = {}
    for goal in goals:
        # We don't need to re-calculate if the goal's subproof is already memoized.
        if goal in sub_proof:
            goal_is_proven[goal] = True
            continue
        try:
            proof_of_goal = _proof_of_predicate(goal, proof_state, sub_proof)
            goal_is_proven[goal] = True
        except JustificationError:
            # Could not justify this goal, so we skip it
            goal_is_proven[goal] = False
            continue
        for proof_step in proof_of_goal:
            if proof_step not in proof_steps:
                proof_steps.append(proof_step)
    return tuple(proof_steps), goal_is_proven


def _proof_of_predicate(
    predicate: Predicate,
    proof_state: ProofState,
    sub_proof: dict[Predicate, tuple[Justification, ...]],
) -> tuple[Justification, ...]:
    stack: list[Predicate] = [predicate]
    while stack:
        current_predicate = stack[-1]  # Peek
        if current_predicate in sub_proof:
            stack.pop()
            continue

        justification = _get_justification_of_predicate(current_predicate, proof_state)
        premises = justify_dependency(justification, proof_state)
        unresolved_premises = [p for p in premises if p not in sub_proof]

        if not unresolved_premises:
            stack.pop()
            cur_proof: tuple[Justification, ...] = ()
            for p in premises:
                # Reconstruct the full subproof for the premise
                p_dep = _get_justification_of_predicate(p, proof_state)
                premise_full_proof = sub_proof[p] + (p_dep,)
                cur_proof += tuple(
                    dep for dep in premise_full_proof if dep not in cur_proof
                )
            sub_proof[current_predicate] = cur_proof
        else:
            stack.extend(unresolved_premises)

    return sub_proof[predicate] + (proof_state.graph.hyper_graph[predicate],)


def _get_justification_of_predicate(
    predicate: Predicate, proof_state: ProofState
) -> Justification:
    justification = proof_state.graph.hyper_graph.get(predicate)
    if justification is None:
        LOGGER.debug(f"Justification not found for {predicate}.")
        justification = proof_state.justify(predicate)
    return justification
