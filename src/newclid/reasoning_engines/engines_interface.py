from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NamedTuple

from newclid.dependencies.dependency_building import DependencyBody
from newclid.statements.statement import Statement

if TYPE_CHECKING:
    from newclid.dependencies.dependency import Dependency


class Derivation(NamedTuple):
    statement: Statement
    dep_body: DependencyBody


class ReasoningEngine(ABC):
    @abstractmethod
    def ingest(self, dependency: "Dependency"):
        """Ingest a new dependency from the core reasoning engine."""

    @abstractmethod
    def resolve(self, **kwargs) -> list[Derivation]:
        """Deduces new statements and their initialized dependencies."""
