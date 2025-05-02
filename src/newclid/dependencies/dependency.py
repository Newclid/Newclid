from __future__ import annotations
import logging
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from newclid.statement import Statement

LOGGER = logging.getLogger(__name__)


NUMERICAL_CHECK = "Numerical Check"
IN_PREMISES = "Premise"


class NumericalyFalseDependencyError(Exception):
    """Raised if adding a numericaly false dependency"""


class Dependency(NamedTuple):
    """Dependency is a directed hyper-edge of the StatementsHyperGraph.

    It links a statement to a list of statements that justify it
    and their own dependencies.

    .. image:: ../_static/images/dependency_building/dependency_structure.svg

    """

    statement: Statement
    reason: str
    why: tuple[Statement, ...]

    def add(self):
        if not self.statement.check_numerical():
            raise NumericalyFalseDependencyError(
                f"Added dependency {self.pretty()} the conclusion of which is numerically false"
            )
        dep_graph = self.statement.dep_graph
        if self.statement in dep_graph.hyper_graph:
            return
        dep_graph.hyper_graph[self.statement] = self
        self.statement.predicate.add(self)

    def with_new(self, statement: Statement) -> Dependency:
        return Dependency(statement, self.reason, self.why)

    @classmethod
    def mk(
        cls, statement: Statement, reason: str, why: tuple[Statement, ...]
    ) -> Dependency:
        why = tuple(sorted(set(why), key=lambda x: repr(x)))
        return Dependency(statement, reason, why)

    def pretty(self):
        return f"{self.statement.pretty()} <={self.reason} {', '.join(s.pretty() for s in self.why)}"
