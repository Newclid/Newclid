"""Graph linking predicates by justifications as edges."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Collection

from pyvis.network import Network  # type: ignore

from newclid.justifications._index import JustificationType
from newclid.justifications.justification import justify_dependency
from newclid.proof_justifications import goals_justifications
from newclid.tools import add_edge, boring_predicate

if TYPE_CHECKING:
    from newclid.justifications.justification import Justification
    from newclid.predicates import Predicate
    from newclid.proof_state import ProofState


LOGGER = logging.getLogger(__name__)


class PredicatesGraph:
    """Hyper graph linking predicates by justifications as hyper-edges."""

    def __init__(self) -> None:
        self.hyper_graph: dict[Predicate, Justification] = {}

    def has_edge(self, justification: Justification):
        return self.hyper_graph.get(justification.predicate) == justification

    @property
    def predicates(self) -> list[Predicate]:
        return list(self.hyper_graph.keys())

    def premises(self) -> list[Justification]:
        premises: list[Justification] = []
        for _, justification in self.hyper_graph.items():
            if justification.dependency_type == JustificationType.ASSUMPTION:
                premises.append(justification)
        return premises

    def save_pyvis(
        self, *, proof_state: ProofState, path: Path, stars: Collection[Predicate] = []
    ):
        if stars:
            justifications, _ = goals_justifications(list(stars), proof_state)
        else:
            justifications = tuple(dep for _, dep in self.hyper_graph.items())
        net = Network("1080px", directed=True)
        for justification in justifications:
            if boring_predicate(justification.predicate):
                continue
            shape = "dot"
            color = "#97c2fc"
            if justification.predicate in stars:
                shape = "star"
                color = "gold"
            net.add_node(  # type: ignore
                str(justification.predicate),
                title=f"{justification.dependency_type.value}",
                shape=shape,
                color=color,
                size=10,
            )
        for justification in justifications:
            if boring_predicate(justification.predicate):
                continue
            for premise in justify_dependency(justification, proof_state):
                add_edge(net, str(premise), str(justification.predicate))  # type: ignore
        net.options.layout = {  # type: ignore
            "hierarchical": {
                "enabled": True,
                "direction": "LR",
                "sortMethod": "directed",
            },
        }
        net.show_buttons(filter_=["physics", "layout"])  # type: ignore
        net.show(str(path), notebook=False)  # type: ignore
