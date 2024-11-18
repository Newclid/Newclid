from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Optional


from newclid.dependencies.caching import DependencyCache
from newclid.dependencies.dependency import Dependency, Reason
from newclid.dependencies.dependency_building import DependencyBody

from newclid.dependencies.why_predicates import why_dependency
from newclid.statements.checker import StatementChecker
from newclid.statements.statement import Statement
from newclid.symbols_graph import SymbolsGraph
from newclid._lazy_loading import lazy_import


if TYPE_CHECKING:
    import pyvis
    import networkx
    import seaborn


sns: "seaborn" = lazy_import("seaborn")
vis: "pyvis" = lazy_import("pyvis")
nx: "networkx" = lazy_import("networkx")


class WhyHyperGraph:
    """Hyper graph linking statements by dependencies as hyper-edges."""

    def __init__(
        self,
        symbols_graph: "SymbolsGraph",
        statements_checker: "StatementChecker",
        dependency_cache: "DependencyCache",
    ) -> None:
        self.nx_graph = nx.DiGraph()
        self.symbols_graph = symbols_graph
        self.statements_checker = statements_checker
        self.dependency_cache = dependency_cache

    def build_dependency(
        self, statement: "Statement", body: "DependencyBody"
    ) -> "Dependency":
        """Build a Dependency from a statement and a body.

        .. image:: ../_static/Images/dependency_building/build_dependency.svg

        """
        dependency = Dependency(
            statement=statement, why=tuple(body.why), reason=body.reason
        )
        self._add_dependency(dependency)
        return dependency

    def build_resolved_dependency(
        self,
        statement: "Statement",
        use_cache: bool = True,
    ) -> Optional["Dependency"]:
        """Build and resolve a dependency from a statement.

        .. image:: ../_static/Images/dependency_building/build_resolved_dependency.svg

        """
        reason, why = why_dependency(self, statement, use_cache=use_cache)
        if why is not None:
            why = tuple(why)
        dependency = Dependency(statement=statement, why=why, reason=reason)
        self._add_dependency(dependency)
        return dependency

    def build_dependency_from_statement(
        self,
        statement: "Statement",
        why: tuple["Dependency"],
        reason: Optional[Reason] = None,
    ):
        """Build a dependency from a statement a reason
        and a list of other dependencies.

        .. image:: ../_static/Images/dependency_building/build_dependency_from_statement.svg

        """
        return self.build_dependency(statement, DependencyBody(reason=reason, why=why))

    def _add_dependency(self, dependency: Dependency):
        if dependency.statement not in self.nx_graph.nodes:
            self.nx_graph.add_node(dependency.statement)
        if dependency not in self.nx_graph.nodes:
            dep_name = dependency.reason.name if dependency.reason else ""
            self.nx_graph.add_node(dependency, name=dep_name)
        self.nx_graph.add_edge(dependency, dependency.statement)

        if not dependency.why:
            return
        for why_dep in dependency.why:
            if why_dep.statement not in self.nx_graph.nodes:
                self.nx_graph.add_node(why_dep.statement)
            self.nx_graph.add_edge(why_dep.statement, dependency)

    def show_html(self, html_path: Path):
        nt = vis.network.Network("1080px", directed=True)
        # populates the nodes and edges data structures
        vis_graph: "networkx.DiGraph" = nx.DiGraph()

        colors = sns.color_palette("colorblind", n_colors=20)
        dep_index = 0
        for node, data in self.nx_graph.nodes(data=True):
            node_name = self._node_name(node)
            if isinstance(node, Dependency):
                size = 2
                shape = "square"
                label = node.reason.name
                color_index = dep_index % len(colors)
                color = rgba_to_hex(*colors[color_index], a=1.0)
                mass = 0.1
                dep_index += 1
            elif isinstance(node, Statement):
                size = 40
                shape = "box"
                label = node_name
                mass = 1.0
                color = None

            vis_graph.add_node(
                node_name,
                label=label,
                color=color,
                size=size,
                shape=shape,
                mass=mass,
            )

        for u, v, data in self.nx_graph.edges(data=True):
            arrows = {"to": {"enabled": True}}
            font = {"size": 8}

            attached_dependency: Dependency = u if isinstance(u, Dependency) else v
            color = vis_graph.nodes[self._node_name(attached_dependency)]["color"]

            vis_graph.add_edge(
                self._node_name(u),
                self._node_name(v),
                arrows=arrows,
                font=font,
                color=color,
            )

        nt.from_nx(vis_graph)
        nt.options.interaction.hover = True
        nt.options.physics.solver = "hierarchicalRepulsion"
        nt.options.edges.toggle_smoothness("vertical")
        nt.options.layout = {
            "hierarchical": {
                "enabled": True,
                "levelSeparation": 380,
                "nodeSpacing": 340,
                "treeSpacing": 20,
                "sortMethod": "directed",
                "shakeTowards": "roots",
            }
        }

        nt.options.physics.use_hrepulsion(
            {
                "central_gravity": 0,
                "spring_length": 210,
                "spring_strength": 0.145,
                "node_distance": 250,
                "damping": 0.36,
                "avoid_overlap": 0.11,
            }
        )
        nt.show_buttons(filter_=["physics", "layout"])
        nt.show(str(html_path), notebook=False)

    @staticmethod
    def _node_name(node: Statement | Dependency) -> str:
        if isinstance(node, Dependency):
            dep_name = node.reason.name if node.reason else "Dependency"
            return dep_name + f" for {node.statement}"
        if isinstance(node, Statement):
            return str(node)
        raise TypeError


def rgba_to_hex(r, g, b, a=0.5):
    hexes = "%02x%02x%02x%02x" % (
        int(r * 255),
        int(g * 255),
        int(b * 255),
        int(a * 255),
    )
    return f"#{hexes.upper()}"
