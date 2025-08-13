from __future__ import annotations

from abc import ABC, abstractmethod
from fractions import Fraction
from typing import TYPE_CHECKING, Iterator, Literal, Self

from pydantic import BaseModel, model_validator

from newclid.deductors import ARReason
from newclid.justifications._index import JustificationType
from newclid.predicates import Predicate
from newclid.symbols.symbols_registry import SymbolsRegistry

if TYPE_CHECKING:
    from newclid.justifications.justification import Justification


class ARCoefficient(BaseModel):
    """A premise of an AR deduction."""

    coeff: Fraction
    """The coefficient with which the predicate is multiplied to get the final equation for the wanted predicate."""
    lhs_terms: dict[str, Fraction]
    """The left-hand side terms of the equation in the table."""

    def __hash__(self) -> int:
        return hash((self.coeff, tuple(sorted(self.lhs_terms.items()))))


class ARPremise(BaseModel):
    """A premise of an AR deduction."""

    predicate: Predicate
    """The predicate construction of the premise."""
    coefficient: ARCoefficient
    """The coefficient of the premise."""

    def __hash__(self) -> int:
        return hash((self.predicate, self.coefficient))


class ARDeduction(BaseModel):
    predicate: Predicate
    """The predicate justified by the AR deduction."""
    ar_reason: ARReason
    """The reason for the AR deduction."""
    ar_premises: tuple[ARPremise, ...] | None = None
    """The AR premises of the AR deduction."""

    dependency_type: Literal[JustificationType.AR_DEDUCTION] = (
        JustificationType.AR_DEDUCTION
    )

    @model_validator(mode="after")
    def canonicalize(self) -> Self:
        if self.ar_premises is not None:
            self.ar_premises = tuple(
                sorted(set(self.ar_premises), key=lambda x: repr(x))
            )
        return self

    def __str__(self) -> str:
        premises_txt = ""
        if self.ar_premises is not None:
            premises_txt = (
                ", ".join(str(premise.predicate) for premise in self.ar_premises) + " "
            )
        return f"{premises_txt}=({self.ar_reason.value})> {self.predicate}"

    def __hash__(self) -> int:
        return hash(self.predicate)


class Deductor(ABC):
    @abstractmethod
    def deduce(self, symbols_registry: SymbolsRegistry) -> Iterator[Justification]:
        """Deduce dependencies o new predicates from the current dependency graph."""

    @abstractmethod
    def add_dependency(
        self, dependency: Justification, symbols_registry: SymbolsRegistry
    ) -> None:
        """Add a predicate to the deductor."""

    @abstractmethod
    def check_predicate(
        self, predicate: Predicate, symbols_registry: SymbolsRegistry
    ) -> bool:
        """Check if a predicate is valid for the deductor."""

    @abstractmethod
    def justify_predicate(
        self, predicate: Predicate, symbols_registry: SymbolsRegistry
    ) -> Justification | None:
        """Justify a predicate with a dependency."""


def add_to_deductors(
    dependency: Justification,
    deductors: list[Deductor],
    symbols_registry: SymbolsRegistry,
) -> None:
    for deductor in deductors:
        deductor.add_dependency(dependency, symbols_registry)


def check_from_deductors(
    predicate: Predicate, deductors: list[Deductor], symbols_registry: SymbolsRegistry
) -> bool:
    for deductor in deductors:
        if deductor.check_predicate(predicate, symbols_registry):
            return True
    return False


def justify_from_deductors(
    predicate: Predicate, deductors: list[Deductor], symbols_registry: SymbolsRegistry
) -> Justification | None:
    for deductor in deductors:
        why_dep = deductor.justify_predicate(predicate, symbols_registry)
        if why_dep is not None:
            return why_dep
    return None
