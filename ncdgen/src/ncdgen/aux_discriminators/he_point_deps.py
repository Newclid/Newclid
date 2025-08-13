from newclid.agent.follow_deductions import DeductionType, FollowDeductions
from newclid.justifications.justification import Justification
from newclid.tools import point_construction_tuple

from ncdgen.aux_discriminators._interface import (
    AuxDiscriminator,
    PointsForConclusion,
    predicate_point_names,
)
from ncdgen.build_diagram import Diagram


class AuxFromHEPointsDeps(AuxDiscriminator):
    def goals_with_aux_setup_split(
        self, diagram: Diagram
    ) -> dict[Justification, PointsForConclusion]:
        if not isinstance(diagram.solver.deductive_agent, FollowDeductions):
            raise ValueError(
                "FollowDeductions agent is required to extract subproblems from cached deductions."
            )
        return _get_aux_deps_from_cached_deductions(diagram.solver.deductive_agent)


def _get_aux_deps_from_cached_deductions(
    agent: FollowDeductions,
) -> dict[Justification, PointsForConclusion]:
    aux_deps: dict[Justification, PointsForConclusion] = {}
    for deduction, deps in agent.deps_of_deduction.items():
        match deduction.deduction_type:
            case DeductionType.NUM | DeductionType.REFLEXIVITY:
                continue
            case DeductionType.RULE | DeductionType.AR:
                for dep in deps:
                    aux_deps[dep] = _aux_points_for_conclusion(
                        dep, deduction.point_deps
                    )
    return aux_deps


def _aux_points_for_conclusion(
    dep: Justification, point_deps: list[str]
) -> PointsForConclusion:
    point_names = predicate_point_names(dep.predicate)
    setup_points: set[str] = set()
    aux_points: set[str] = set()
    for required_point in point_deps:
        if all(
            point_construction_tuple(required_point)
            > point_construction_tuple(point_in_conclusion)
            for point_in_conclusion in point_names
        ):
            aux_points.add(required_point)
        else:
            setup_points.add(required_point)
    return PointsForConclusion(setup_points=setup_points, aux_points=aux_points)
