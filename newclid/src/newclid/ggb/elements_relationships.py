from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from newclid.ggb.read_elements import GGBConic, GGBLine, GGBPoint


class RelationShipType(Enum):
    Parallel = "parallel"
    Orthogonal = "orthogonal"
    BisectorLine = "bisector_line"
    BisectorPoint = "bisector_point"
    Tangent = "tangent"
    Congruent = "congruent"
    Cyclic = "cyclic"
    Collinear = "collinear"


class ParaRelationship(BaseModel):
    line: GGBLine
    parallel_to: GGBLine
    relationship_type: Literal[RelationShipType.Parallel] = RelationShipType.Parallel


class OrthoRelationship(BaseModel):
    line: GGBLine
    orthogonal_to: GGBLine
    relationship_type: Literal[RelationShipType.Orthogonal] = (
        RelationShipType.Orthogonal
    )


class BisectorLineRelationship(BaseModel):
    line: GGBLine
    bisector_1: GGBLine
    bisector_2: GGBLine
    relationship_type: Literal[RelationShipType.BisectorLine] = (
        RelationShipType.BisectorLine
    )


class BisectorPointRelationship(BaseModel):
    line: GGBLine
    angle_a: GGBPoint
    angle_vertex: GGBPoint
    angle_b: GGBPoint
    relationship_type: Literal[RelationShipType.BisectorPoint] = (
        RelationShipType.BisectorPoint
    )


class TangentRelationship(BaseModel):
    line: GGBLine
    tangent_to: GGBConic
    relationship_type: Literal[RelationShipType.Tangent] = RelationShipType.Tangent


ElementsRelationships = Annotated[
    ParaRelationship
    | OrthoRelationship
    | TangentRelationship
    | BisectorLineRelationship
    | BisectorPointRelationship,
    Field(discriminator="relationship_type"),
]
