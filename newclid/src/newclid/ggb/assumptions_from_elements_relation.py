import itertools
from typing import cast

from newclid.ggb.elements_relationships import (
    BisectorLineRelationship,
    BisectorPointRelationship,
    ElementsRelationships,
    OrthoRelationship,
    ParaRelationship,
    RelationShipType,
    TangentRelationship,
)
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.problem import PredicateConstruction


def relationships_to_newclid_assumptions(
    relationships: list[ElementsRelationships],
) -> list[PredicateConstruction]:
    assumptions: list[PredicateConstruction] = []
    for relationship in relationships:
        assumptions.extend(_relationship_to_newclid_assumptions(relationship))
    return assumptions


def _relationship_to_newclid_assumptions(
    relationship: ElementsRelationships,
) -> list[PredicateConstruction]:
    match relationship.relationship_type:
        case RelationShipType.Parallel:
            return _para_relationship_to_newclid_assumptions(relationship)
        case RelationShipType.Orthogonal:
            return _ortho_relationship_to_newclid_assumptions(relationship)
        case RelationShipType.BisectorLine:
            return _bisector_line_relationship_to_newclid_assumptions(relationship)
        case RelationShipType.BisectorPoint:
            return _bisector_point_relationship_to_newclid_assumptions(relationship)
        case RelationShipType.Tangent:
            return _tangent_relationship_to_newclid_assumptions(relationship)
    raise NotImplementedError(f"Unknown relationship: {relationship}")


def _para_relationship_to_newclid_assumptions(
    relationship: ParaRelationship,
) -> list[PredicateConstruction]:
    para_predicates: list[PredicateConstruction] = []
    for first_args in itertools.combinations(relationship.line.points, 2):
        for second_args in itertools.combinations(relationship.parallel_to.points, 2):
            first_pred_args = tuple(PredicateArgument(a) for a in first_args)
            second_pred_args = tuple(PredicateArgument(a) for a in second_args)
            para_predicates.append(
                PredicateConstruction.from_predicate_type_and_args(
                    PredicateType.PARALLEL, (*first_pred_args, *second_pred_args)
                )
            )
    return para_predicates


def _ortho_relationship_to_newclid_assumptions(
    relationship: OrthoRelationship,
) -> list[PredicateConstruction]:
    perp_predicates: list[PredicateConstruction] = []
    if len(relationship.line.points) > 1 and len(relationship.orthogonal_to.points) > 1:
        a, b = relationship.line.points[:2]
        c, d = relationship.orthogonal_to.points[:2]
        perp_predicates.append(
            PredicateConstruction.from_predicate_type_and_args(
                PredicateType.PERPENDICULAR,
                cast(tuple[PredicateArgument, ...], (a, b, c, d)),
            )
        )
    return perp_predicates


def _bisector_line_relationship_to_newclid_assumptions(
    relationship: BisectorLineRelationship,
) -> list[PredicateConstruction]:
    eqangle_predicates: list[PredicateConstruction] = []
    if (
        len(relationship.bisector_1.points) > 1
        and len(relationship.line.points) > 1
        and len(relationship.bisector_2.points) > 1
    ):
        a, b = relationship.bisector_1.points[:2]
        c, d = relationship.line.points[:2]
        g, h = relationship.bisector_2.points[:2]
        eqangle_predicates.append(
            PredicateConstruction.from_predicate_type_and_args(
                PredicateType.EQUAL_ANGLES,
                cast(tuple[PredicateArgument, ...], (a, b, c, d, c, d, g, h)),
            )
        )
    return eqangle_predicates


def _bisector_point_relationship_to_newclid_assumptions(
    relationship: BisectorPointRelationship,
) -> list[PredicateConstruction]:
    eqangle_predicates: list[PredicateConstruction] = []
    if len(relationship.line.points) > 1:
        a = relationship.angle_a.label
        b = relationship.angle_vertex.label
        c = relationship.angle_b.label
        d = next((point for point in relationship.line.points if point != b), None)
        if all(x is not None for x in (a, b, c, d)):
            eqangle_predicates.append(
                PredicateConstruction.from_predicate_type_and_args(
                    PredicateType.EQUAL_ANGLES,
                    cast(tuple[PredicateArgument, ...], (a, b, b, d, b, d, b, c)),
                )
            )
    return eqangle_predicates


def _tangent_relationship_to_newclid_assumptions(
    relationship: TangentRelationship,
) -> list[PredicateConstruction]:
    conic = relationship.tangent_to
    perp_predicates: list[PredicateConstruction] = []
    if conic.center is not None:
        for point in set(relationship.line.points).intersection(conic.points):
            point_in_line = next(
                (p for p in relationship.line.points if p != point), None
            )
            if point_in_line is not None:
                perp_predicates.append(
                    PredicateConstruction.from_predicate_type_and_args(
                        PredicateType.PERPENDICULAR,
                        cast(
                            tuple[PredicateArgument, ...],
                            (point, conic.center, point, point_in_line),
                        ),
                    )
                )
    return perp_predicates
