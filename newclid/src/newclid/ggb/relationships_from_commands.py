from newclid.ggb.elements_relationships import (
    BisectorLineRelationship,
    BisectorPointRelationship,
    ElementsRelationships,
    OrthoRelationship,
    ParaRelationship,
    TangentRelationship,
)
from newclid.ggb.read_commands import GGBCommand, GGBReadCommandType
from newclid.ggb.read_elements import GGBConic, GGBLine, GGBPoint


def relationships_from_commands(
    commands: list[GGBCommand],
    points: dict[str, GGBPoint],
    lines: dict[str, GGBLine],
    conics: dict[str, GGBConic],
) -> list[ElementsRelationships]:
    relationships: list[ElementsRelationships] = []
    for command in commands:
        relationships.extend(
            _relationships_from_command(command, points, lines, conics)
        )
    return relationships


def _relationships_from_command(
    command: GGBCommand,
    points: dict[str, GGBPoint],
    lines: dict[str, GGBLine],
    conics: dict[str, GGBConic],
) -> list[ElementsRelationships]:
    match command.construction_type:
        case GGBReadCommandType.OrthogonalLine:
            return [
                OrthoRelationship(
                    line=lines[command.perpendicular_line],
                    orthogonal_to=lines[command.line],
                )
            ]
        case GGBReadCommandType.ParallelLine:
            return [
                ParaRelationship(
                    line=lines[command.base_line],
                    parallel_to=lines[command.parallel_line],
                )
            ]
        case GGBReadCommandType.AngularBisector:
            return [
                BisectorLineRelationship(
                    line=lines[command.line_bisector],
                    bisector_1=lines[command.line_1],
                    bisector_2=lines[command.line_2],
                )
            ]
        case GGBReadCommandType.AngularBisectorPoints:
            return [
                BisectorPointRelationship(
                    line=lines[command.line_bisector],
                    angle_a=points[command.point_a],
                    angle_vertex=points[command.corner],
                    angle_b=points[command.point_b],
                )
            ]
        case GGBReadCommandType.TangentOnCircle:
            return [
                TangentRelationship(
                    line=lines[command.tangent_line],
                    tangent_to=conics[command.tangent_object],
                )
            ]
        case GGBReadCommandType.TangentOutsideCircle:
            return [
                TangentRelationship(
                    line=lines[command.tangent_line1],
                    tangent_to=conics[command.tangent_object],
                ),
                TangentRelationship(
                    line=lines[command.tangent_line2],
                    tangent_to=conics[command.tangent_object],
                ),
            ]
        case _:
            return []
