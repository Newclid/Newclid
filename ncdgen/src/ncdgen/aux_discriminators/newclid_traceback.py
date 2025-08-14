from newclid.justifications.justification import Justification, justify_dependency
from newclid.predicates import Predicate
from newclid.proof_state import ProofState

from ncdgen.aux_discriminators._interface import (
    AuxDiscriminator,
    PointsForConclusion,
    predicate_point_names,
)
from ncdgen.build_diagram import Diagram


class AuxFromNewclidTraceback(AuxDiscriminator):
    def goals_with_aux_setup_split(
        self, diagram: Diagram
    ) -> dict[Justification, PointsForConclusion]:
        goals_with_aux: dict[Justification, PointsForConclusion] = {}
        for goal in diagram.solver.proof_state.graph.hyper_graph.values():
            goals_with_aux[goal] = _get_setup_aux_points(
                goal.predicate,
                point_requirements=diagram.setup_graph,
                proof_state=diagram.solver.proof_state,
            )
        return goals_with_aux


def _get_setup_aux_points(
    predicate: Predicate,
    point_requirements: dict[str, set[str]],
    proof_state: ProofState,
) -> PointsForConclusion:
    """Get the sets of setup and auxiliary points for a given dependency."""
    setup_points = predicate_point_names(predicate)
    for setup_point in setup_points.copy():
        setup_points.update(point_requirements[setup_point])
    proof_points = _get_all_dep_points(predicate, proof_state)
    for proof_point in proof_points.copy():
        proof_points.update(point_requirements[proof_point])
    aux_points = proof_points.difference(setup_points)
    return PointsForConclusion(setup_points=setup_points, aux_points=aux_points)


def _get_all_dep_points(predicate: Predicate, proof_state: ProofState) -> set[str]:
    # do a simple dfs to get all points in the dependency subtree
    points: set[str] = set()
    visited: set[Predicate] = set()

    def dfs(node: Predicate):
        if node in visited:
            return
        visited.add(node)
        points.update(predicate_point_names(node))
        justification = proof_state.justify(node)
        if not justification:
            return

        for pred_predicate in justify_dependency(justification, proof_state):
            dfs(pred_predicate)

    dfs(predicate)
    # filter out numerical constants (like 3pi/4)
    return set([p for p in points if not p[0].isdigit()])
