# from __future__ import annotations

# from collections import defaultdict
# from typing import Iterator

# from newclid.agent.follow_deductions import CachedDeduction
# from newclid.deductors.deductor_interface import Deductor
# from newclid.justifications.justification import NOT_A_DEDUCTION_REASONS, Justification
# from newclid.justifications.predicates_graph import JustificationGraph
# from newclid.yuclid_adapter import YuclidAdapter
# from newclid.problem import NcProblem, StatementConstruction
# from newclid.proof_state import ProofState
# from newclid.predicates import Predicate
# from newclid.problem import predicate_to_construction


# class OmniARDeductor(Deductor):
#     def __init__(self, he_adapter: YuclidAdapter) -> None:
#         self._he_adapter = he_adapter
#         self._given_predicates: set[StatementConstruction] = set()
#         self._new_available_ar_deductions: list[CachedDeduction] = []
#         self._proven_predicates: dict[StatementConstruction, Justification] = {}
#         self._premise_to_deductions: dict[
#             StatementConstruction, list[CachedDeduction]
#         ] = defaultdict(list)

#     def deduce(
#         self, pred_graph: JustificationGraph, deductors: list[Deductor]
#     ) -> Iterator[Justification]:
#         new_deductions = self._new_available_ar_deductions.copy()
#         self._new_available_ar_deductions.clear()
#         for ar_deduction in new_deductions:
#             for conclusion in ar_deduction.conclusions:
#                 if conclusion in self._proven_predicates:
#                     yield self._proven_predicates[conclusion]

#     def add_dependency(self, dependency: Justification) -> None:
#         new_predicate = predicate_to_construction(dependency.predicate)
#         if new_predicate in self._proven_predicates:
#             return
#         self._given_predicates.add(new_predicate)
#         if dependency.reason in NOT_A_DEDUCTION_REASONS:
#             # Do not trigger deductions while constructing the proof state
#             return
#         self._trigger_deductions(new_predicate, proof_state)

#     def check_predicate(self, predicate: Statement) -> bool:
#         self._trigger_deductions(predicate)
#         return (
#             self._proven_predicates.get(predicate_to_construction(predicate))
#             is not None
#         )

#     def justify_predicate(self, predicate: Statement) -> Justification | None:
#         self._trigger_deductions(predicate)
#         return self._proven_predicates.get(predicate_to_construction(predicate))

#     def _compute_premise_to_deductions(
#         self, problem: NcProblem
#     ) -> list[CachedDeduction]:
#         all_deductions = self._he_adapter.ar_deductions(problem)
#         for ar_deduction in all_deductions:
#             for premise in ar_deduction.premises:
#                 self._premise_to_deductions[premise].append(ar_deduction)
#         return all_deductions

#     def _trigger_deductions(
#         self, new_predicate: Statement, proof_state: ProofState
#     ) -> None:
#         if not self._premise_to_deductions:
#             all_deductions = self._compute_premise_to_deductions(proof_state.problem)
#             for ar_deduction in all_deductions:
#                 self._try_apply_ar_deduction(ar_deduction)
#             return
#         for ar_deduction in self._premise_to_deductions[
#             predicate_to_construction(new_predicate)
#         ]:
#             self._try_apply_ar_deduction(ar_deduction)

#     def _try_apply_ar_deduction(self, ar_deduction: CachedDeduction) -> None:
#         can_apply = all(
#             premise in self._given_predicates for premise in ar_deduction.premises
#         )
#         if not can_apply:
#             return
#         self._new_available_ar_deductions.append(ar_deduction)
#         for conclusion in ar_deduction.conclusions:
#             self._proven_predicates[conclusion.predicate] = conclusion
