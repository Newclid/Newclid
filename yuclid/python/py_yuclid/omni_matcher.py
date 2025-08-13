from __future__ import annotations

from typing import TYPE_CHECKING

from newclid.agent.follow_deductions import CachedRuleDeduction
from newclid.justifications.justification import Justification
from newclid.predicates import Predicate, predicate_from_construction
from newclid.rule import Rule, RuleApplication
from newclid.rule_matching.interface import RuleMatcher
from newclid.symbols.symbols_registry import SymbolsRegistry

from py_yuclid.yuclid_adapter import YuclidAdapter

if TYPE_CHECKING:
    from newclid.proof_state import ProofState


class OmniMatcher(RuleMatcher):
    def __init__(self, he_adapter: YuclidAdapter):
        self._he_adapter = he_adapter

    def match_theorem(self, rule: Rule, proof: ProofState) -> set[Justification]:
        justified_conclusions: set[Justification] = set()
        for rule_deduction in self._he_adapter.rule_matches(rule, proof.problem):
            can_apply = True
            premises_predicates: list[Predicate] = []
            for premise in rule_deduction.premises:
                predicate = predicate_from_construction(
                    premise, points_registry=proof.symbols.points
                )
                if predicate is None:
                    raise ValueError(f"Could not build Statement from '{premise}'")
                if not proof.check(predicate):
                    can_apply = False
                    break
            if not can_apply:
                continue

            justifications_from_conclusions = (
                _justifications_from_conclusions_of_deduction(
                    rule_deduction,
                    symbols_registry=proof.symbols,
                    premises_predicates=premises_predicates,
                )
            )
            justified_conclusions.update(justifications_from_conclusions)
        return justified_conclusions


def _justifications_from_conclusions_of_deduction(
    deduction: CachedRuleDeduction,
    symbols_registry: SymbolsRegistry,
    premises_predicates: list[Predicate],
) -> list[Justification]:
    justifications_from_conclusions: list[Justification] = []
    for conclusion in deduction.conclusions:
        predicate = predicate_from_construction(
            conclusion, points_registry=symbols_registry.points
        )
        if predicate is None:
            raise ValueError(f"Could not build Statement from '{conclusion}'")

        justifications_from_conclusions.append(
            RuleApplication(
                predicate=predicate,
                rule=deduction.rule,
                premises=tuple(premises_predicates),
            )
        )
    return justifications_from_conclusions
