from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Literal, cast

from pydantic import BaseModel, Field

from newclid.deductors.deductor_interface import ARDeduction
from newclid.justifications._index import JustificationType
from newclid.predicates import Predicate
from newclid.rule import RuleApplication
from newclid.symbols.circles_registry import CircleMerge
from newclid.symbols.lines_registry import LineMerge

if TYPE_CHECKING:
    from newclid.proof_state import ProofState

LOGGER = logging.getLogger(__name__)


class Assumption(BaseModel):
    predicate: Predicate
    """The predicate justified by assumption."""

    dependency_type: Literal[JustificationType.ASSUMPTION] = (
        JustificationType.ASSUMPTION
    )

    def __hash__(self) -> int:
        return hash(self.predicate)


class NumericalCheck(BaseModel):
    predicate: Predicate
    """The predicate justified by numerical check."""

    dependency_type: Literal[JustificationType.NUMERICAL_CHECK] = (
        JustificationType.NUMERICAL_CHECK
    )

    def __hash__(self) -> int:
        return hash(self.predicate)


class Reflexivity(BaseModel):
    predicate: Predicate
    """The predicate trivially true by reflexivity."""

    dependency_type: Literal[JustificationType.REFLEXIVITY] = (
        JustificationType.REFLEXIVITY
    )

    def __hash__(self) -> int:
        return hash(self.predicate)


class DirectConsequence(BaseModel):
    predicate: Predicate
    """The predicate justified by the direct consequences."""
    premises: tuple[Predicate, ...]
    """The premises of the direct consequences."""

    dependency_type: Literal[JustificationType.DIRECT_CONSEQUENCE] = (
        JustificationType.DIRECT_CONSEQUENCE
    )

    def __hash__(self) -> int:
        return hash(self.predicate)


Justification = Annotated[
    Assumption
    | NumericalCheck
    | RuleApplication
    | ARDeduction
    | CircleMerge
    | LineMerge
    | DirectConsequence
    | Reflexivity,
    Field(discriminator="dependency_type"),
]


def justify_dependency(
    dep: Justification, proof_state: ProofState
) -> tuple[Predicate, ...]:
    match dep.dependency_type:
        case (
            JustificationType.ASSUMPTION
            | JustificationType.NUMERICAL_CHECK
            | JustificationType.REFLEXIVITY
        ):
            return ()
        case JustificationType.LINE_MERGE | JustificationType.CIRCLE_MERGE:
            return (dep.direct_justification,)
        case JustificationType.RULE_APPLICATION | JustificationType.DIRECT_CONSEQUENCE:
            return dep.premises
        case JustificationType.AR_DEDUCTION:
            if dep.ar_premises is not None:
                return tuple(premise.predicate for premise in dep.ar_premises)

            ar_justification = cast(ARDeduction, proof_state.justify(dep.predicate))
            if ar_justification.ar_premises is None:
                raise ValueError(
                    f"Could not find premises for AR deduction: {dep.predicate}"
                )
            dep.ar_premises = tuple(
                sorted(set(ar_justification.ar_premises), key=lambda x: repr(x))
            )
            return tuple(premise.predicate for premise in dep.ar_premises)
    raise ValueError(f"Unknown dependency type: {dep.dependency_type}")
