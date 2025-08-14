from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from newclid.predicate_types import PredicateArgument
    from newclid.proof_state import ProofState
    from newclid.symbols.symbols_registry import LineOrCircle, SymbolsRegistry


class PredicateInterface(ABC, BaseModel):
    """
    When the args are passed in functions other than parse and to_tokens,
    the orders are guaranteed to be canonique.
    """

    @staticmethod
    @abstractmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        """Preparse the predicate arguments."""

    @abstractmethod
    def check_numerical(self) -> bool:
        """Check numerically the predicate."""

    @abstractmethod
    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        """Convert the predicate to a tuple of strings."""

    def add(self, proof_state: ProofState) -> tuple[PredicateInterface, ...]:
        """Add the predicate to the proof state.

        Return a tuple of predicates that are direct consequences of the predicate by definition.
        """
        return ()

    def check(self, proof_state: ProofState) -> bool | None:
        """Check symbolically the predicate in the current proof state.

        If the predicate cannot be decided, return None.
        """
        return None

    def symbols(self, symbols: SymbolsRegistry) -> tuple[LineOrCircle, ...]:
        """Make symbols for the predicate in the symbols graph."""
        return ()

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self) -> str:
        return f"{self.predicate_type.value} {' '.join(self.to_tokens())}"  # type: ignore


class NumericalPredicate(PredicateInterface):
    """Predicate that can only be checked numerically."""

    def check(self, proof_state: ProofState) -> bool:
        """Numerical predicates are always true symbolically."""
        return True
