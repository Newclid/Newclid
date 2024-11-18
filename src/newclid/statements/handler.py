from newclid.dependencies.caching import DependencyCache
from newclid.dependencies.why_graph import WhyHyperGraph
from newclid.statements.adder import IntrinsicRules, StatementAdder
from newclid.statements.checker import StatementChecker
from newclid.statements.enumerator import StatementsEnumerator
from newclid.symbols_graph import SymbolsGraph


class StatementsHandler:
    def __init__(
        self,
        symbols_graph: "SymbolsGraph",
        dependency_cache: "DependencyCache",
        disabled_intrinsic_rules: list[IntrinsicRules],
    ) -> None:
        self.checker = StatementChecker(symbols_graph)
        self.graph = WhyHyperGraph(
            symbols_graph=symbols_graph,
            statements_checker=self.checker,
            dependency_cache=dependency_cache,
        )
        self.adder = StatementAdder(
            symbols_graph=symbols_graph,
            statements_graph=self.graph,
            statements_checker=self.checker,
            dependency_cache=dependency_cache,
            disabled_intrinsic_rules=disabled_intrinsic_rules,
        )
        self.enumerator = StatementsEnumerator(symbols_graph, self.checker)
