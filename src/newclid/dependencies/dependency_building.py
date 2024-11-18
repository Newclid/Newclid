from __future__ import annotations
from typing import TYPE_CHECKING


from newclid.dependencies.dependency import Reason, Dependency

if TYPE_CHECKING:
    from newclid.statements.statement import Statement
    from newclid.dependencies.why_graph import WhyHyperGraph


class DependencyBody:
    """Statement-less body of a dependency that can be extended
    before becoming a dependency."""

    def __init__(self, reason: Reason, why: tuple[Dependency]):
        assert isinstance(reason, Reason)
        self.reason: Reason = reason
        self.why: tuple[Dependency] = tuple(why)

    def build(
        self, statements_graph: "WhyHyperGraph", statement: Statement
    ) -> Dependency:
        """Build a Dependency by attaching a statement to a body.

        .. image:: ../_static/Images/dependency_building/build_dependency.svg

        """
        return statements_graph.build_dependency(statement, body=self)

    def extend(
        self,
        statements_graph: "WhyHyperGraph",
        statement: "Statement",
        extention_statement: "Statement",
        extention_reason: Reason,
    ) -> "DependencyBody":
        """Extend a new body from a dependency with a new statement given a reason.

        .. image:: ../_static/Images/dependency_building/extend.svg

        """
        extension_dep = statements_graph.build_resolved_dependency(extention_statement)
        if extension_dep is None:
            raise
        return DependencyBody(
            reason=extention_reason,
            why=(self.build(statements_graph, statement), extension_dep),
        )

    def extend_many(
        self,
        statements_graph: "WhyHyperGraph",
        original_statement: "Statement",
        extention_statements: list["Statement"],
        extention_reason: Reason,
    ) -> "DependencyBody":
        """Extend a new body from a dependency with
        many a new statements given a reason.

        .. image:: ../_static/Images/dependency_building/extend_many.svg

        """
        if not extention_statements:
            return self
        extended_dep = [
            statements_graph.build_resolved_dependency(e_statement)
            for e_statement in extention_statements
        ]
        return DependencyBody(
            reason=extention_reason,
            why=(self.build(statements_graph, original_statement), *extended_dep),
        )

    def extend_by_why(
        self,
        statements_graph: "WhyHyperGraph",
        original_statement: "Statement",
        why: list[Dependency],
        extention_reason: Reason,
    ) -> "DependencyBody":
        """Extend a new body from a dependency given a reason
        and a list of other dependencies.

        .. image:: ../_static/Images/dependency_building/extend_by_why.svg

        """
        if not why:
            return self
        return DependencyBody(
            reason=extention_reason,
            why=(self.build(statements_graph, original_statement), *why),
        )

    def copy(self) -> "DependencyBody":
        return DependencyBody(reason=self.reason, why=self.why)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, DependencyBody):
            return False
        return self.reason == value.reason and set(self.why) == set(value.why)
