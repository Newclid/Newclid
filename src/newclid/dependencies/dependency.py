from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from typing_extensions import Self

from newclid.theorem import Theorem
from newclid.statements.statement import Statement

if TYPE_CHECKING:
    from newclid.statements.adder import IntrinsicRules
    from newclid.reasoning_engines.algebraic_reasoning import AlgebraicRules


@dataclass(frozen=True)
class Reason:
    object: Theorem | "AlgebraicRules" | "IntrinsicRules" | str
    name: str = ""

    def __post_init__(self):
        if not self.name:
            if isinstance(self.object, Theorem):
                name = self.object.rule_name
            elif isinstance(self.object, str):
                name = self.object
            else:
                name = self.object.value
            object.__setattr__(self, "name", name)

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass(frozen=True)
class Dependency:
    """Dependency is a directed hyper-edge of the StatementsHyperGraph.

    It links a statement to a list of statements that justify it
    and their own dependencies.

    .. image:: ../_static/Images/dependency_building/dependency_structure.svg

    """

    statement: Statement
    why: tuple[Self]
    reason: Optional[Reason] = None

    def __hash__(self) -> int:
        return hash((self.statement, self.reason))
