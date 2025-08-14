from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, Field

from newclid.agent.agents_interface import DeductiveAgent
from newclid.deductors import ARReason
from newclid.deductors.deductor_interface import ARCoefficient, ARPremise
from newclid.justifications.justification import (
    ARDeduction,
    Justification,
    NumericalCheck,
    Reflexivity,
    RuleApplication,
)
from newclid.justifications.predicates_graph import PredicatesGraph
from newclid.predicates import (
    NUMERICAL_PREDICATES,
    Predicate,
    predicate_from_construction,
)
from newclid.problem import PredicateConstruction, ProblemSetup
from newclid.rule import Rule

if TYPE_CHECKING:
    from newclid.proof_state import ProofState

LOGGER = logging.getLogger(__name__)


class DeductionType(str, Enum):
    RULE = "rule"
    AR = "ar"
    NUM = "num"
    REFLEXIVITY = "refl"


class CachedRuleDeduction(BaseModel):
    deduction_type: Literal[DeductionType.RULE] = DeductionType.RULE
    rule: Rule
    premises: tuple[PredicateConstruction, ...]
    conclusions: tuple[PredicateConstruction, ...]
    point_deps: list[str]

    def __hash__(self) -> int:
        return hash((self.rule, self.premises, self.conclusions))


class ARPremiseConstruction(BaseModel):
    predicate_construction: PredicateConstruction
    coefficient: ARCoefficient

    def __hash__(self) -> int:
        return hash((self.predicate_construction, self.coefficient))


class CachedARDeduction(BaseModel):
    deduction_type: Literal[DeductionType.AR] = DeductionType.AR
    ar_reason: ARReason
    premises: tuple[ARPremiseConstruction, ...]
    conclusions: tuple[PredicateConstruction, ...]
    point_deps: list[str]

    def __hash__(self) -> int:
        return hash((self.ar_reason, self.premises, self.conclusions))


class CachedNumericalCheckDeduction(BaseModel):
    deduction_type: Literal[DeductionType.NUM] = DeductionType.NUM
    conclusions: tuple[PredicateConstruction, ...]

    def __hash__(self) -> int:
        return hash(self.conclusions)


class CachedReflexivityDeduction(BaseModel):
    deduction_type: Literal[DeductionType.REFLEXIVITY] = DeductionType.REFLEXIVITY
    conclusions: tuple[PredicateConstruction, ...]

    def __hash__(self) -> int:
        return hash(self.conclusions)


CachedDeduction = Annotated[
    CachedRuleDeduction
    | CachedARDeduction
    | CachedNumericalCheckDeduction
    | CachedReflexivityDeduction,
    Field(discriminator="deduction_type"),
]


class DeductionProvider(ABC):
    @abstractmethod
    def ordered_deductions_for_problem(
        self, problem: ProblemSetup
    ) -> list[CachedDeduction]: ...

    @property
    @abstractmethod
    def precomputation_input_str(self) -> str: ...


class FollowDeductionsStats(BaseModel):
    """Statistics for the FollowDeductions agent."""

    agent_type: Literal["follow_deductions"] = "follow_deductions"

    n_deductions_stored: int
    """The number of deductions stored."""

    n_deductions_followed: int
    """The list of deductions followed."""


class FollowDeductions(DeductiveAgent):
    def __init__(self, deductions_provider: DeductionProvider) -> None:
        self._deductions_provider = deductions_provider
        self._deductions: list[CachedDeduction] = []
        self.premises_of_deduction: dict[CachedDeduction, list[Predicate]] = {}
        self.deps_of_deduction: dict[CachedDeduction, list[Justification]] = {}
        self._has_gathered_deductions = False
        self._stats = FollowDeductionsStats(
            n_deductions_stored=0, n_deductions_followed=0
        )

    def get_stats(self) -> FollowDeductionsStats:
        return self._stats.model_copy()

    def step(self, proof: ProofState, rules: list[Rule]) -> bool:
        if not self._has_gathered_deductions:
            self._gather_deductions(proof)

        if not self._deductions:
            # No more deductions to follow, we're done.
            return False

        next_deduction = self._deductions.pop(0)
        precomputation_input_str = self._deductions_provider.precomputation_input_str
        premises_predicates = self.premises_of_deduction[next_deduction]
        _check_premises_of_deduction(
            next_deduction,
            precomputation_input_str=precomputation_input_str,
            premises_predicates=premises_predicates,
            pred_graph=proof.graph,
        )
        for new_dep in self.deps_of_deduction[next_deduction]:
            LOGGER.debug(f"Proved by following deduction: {new_dep}")
            _success = proof.apply(new_dep)
            self._stats.n_deductions_followed += 1

        return True

    def _gather_deductions(self, proof_state: ProofState) -> None:
        self._deductions = self._deductions_provider.ordered_deductions_for_problem(
            proof_state.problem
        ).copy()
        self._stats.n_deductions_stored = len(self._deductions)
        for deduction in self._deductions:
            self.premises_of_deduction[deduction] = _validate_premises_of_deduction(
                deduction,
                precomputation_input_str=self._deductions_provider.precomputation_input_str,
                proof_state=proof_state,
            )
            self.deps_of_deduction[deduction] = _deps_from_conclusions_of_deduction(
                deduction,
                precomputation_input_str=self._deductions_provider.precomputation_input_str,
                premises_predicates=self.premises_of_deduction[deduction],
                proof_state=proof_state,
            )
        self._has_gathered_deductions = True

    def reset(self) -> None:
        self._deductions = []
        self.premises_of_deduction = {}
        self.deps_of_deduction = {}
        self._has_gathered_deductions = False
        self._stats = FollowDeductionsStats(
            n_deductions_stored=0, n_deductions_followed=0
        )


def _validate_premises_of_deduction(
    deduction: CachedDeduction,
    precomputation_input_str: str,
    proof_state: ProofState,
) -> list[Predicate]:
    match deduction.deduction_type:
        case DeductionType.NUM | DeductionType.REFLEXIVITY:
            return []
        case DeductionType.RULE:
            premises = deduction.premises
        case DeductionType.AR:
            premises = tuple(
                premise.predicate_construction for premise in deduction.premises
            )

    premises_predicates: list[Predicate] = []
    for premise in premises:
        premise_predicate = predicate_from_construction(
            premise, points_registry=proof_state.symbols.points
        )
        if premise_predicate is None:
            error_msg = (
                f"Premise '{premise}' of deduction {deduction} could not be built."
            )
            LOGGER.error(f"{error_msg}.\nSetup:\n{precomputation_input_str}")
            raise ValueError(error_msg)

        if (
            premise_predicate.predicate_type in NUMERICAL_PREDICATES
            and not proof_state.check_numerical(premise_predicate)
        ):
            error_msg = (
                f"Premise '{premise}' is numericaly false within deduction {deduction}."
            )
            LOGGER.error(f"{error_msg}.\nSetup:\n{precomputation_input_str}")
            raise ValueError(error_msg)

        premises_predicates.append(premise_predicate)

    return premises_predicates


def _deps_from_conclusions_of_deduction(
    deduction: CachedDeduction,
    proof_state: ProofState,
    precomputation_input_str: str,
    premises_predicates: list[Predicate],
) -> list[Justification]:
    new_deps: list[Justification] = []
    for conclusion in deduction.conclusions:
        new_predicate = predicate_from_construction(
            conclusion, points_registry=proof_state.symbols.points
        )
        if new_predicate is None:
            error_msg = f"Conclusion {conclusion} could not be built."
            LOGGER.error(f"{error_msg}.\nSetup:\n{precomputation_input_str}")
            raise ValueError(error_msg)

        if not proof_state.check_numerical(new_predicate):
            error_msg = f"Conclusion {new_predicate} is numerical false."
            LOGGER.error(f"{error_msg}.\nSetup:\n{precomputation_input_str}")
            raise ValueError(error_msg)

        if deduction.deduction_type is DeductionType.RULE:
            _check_rule_conclusions(deduction)

        new_dep: Justification
        match deduction.deduction_type:
            case DeductionType.RULE:
                new_dep = RuleApplication(
                    predicate=new_predicate,
                    rule=deduction.rule,
                    premises=tuple(premises_predicates),
                )
            case DeductionType.AR:
                new_dep = ARDeduction(
                    predicate=new_predicate,
                    ar_reason=deduction.ar_reason,
                    ar_premises=tuple(
                        ARPremise(
                            predicate=premise,
                            coefficient=premise_construction.coefficient,
                        )
                        for premise_construction, premise in zip(
                            deduction.premises, premises_predicates
                        )
                    ),
                )
            case DeductionType.NUM:
                new_dep = NumericalCheck(predicate=new_predicate)
            case DeductionType.REFLEXIVITY:
                new_dep = Reflexivity(predicate=new_predicate)

        new_deps.append(new_dep)
    return new_deps


class DoubleCheckError(Exception):
    """A deduction given is not valid to be followed."""


def _check_premises_of_deduction(
    deduction: CachedDeduction,
    precomputation_input_str: str,
    premises_predicates: list[Predicate],
    pred_graph: PredicatesGraph,
) -> None:
    for premise_predicate in premises_predicates:
        premise_justification = pred_graph.hyper_graph.get(premise_predicate)
        if premise_justification is None:
            error_msg = (
                f"Premise '{premise_predicate}' of deduction {deduction} not found"
                " in proof state while following given deductions."
            )
            LOGGER.error(f"{error_msg}.\nSetup:\n{precomputation_input_str}")
            raise DoubleCheckError(error_msg)


def _check_rule_conclusions(deduction: CachedRuleDeduction) -> None:
    """Double check that the deduction is a valid application of the rule."""
    pass
