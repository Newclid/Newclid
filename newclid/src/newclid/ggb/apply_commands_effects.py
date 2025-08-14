from newclid.ggb.read_commands import (
    GGBAngularBisectorLinesCommand,
    GGBAngularBisectorPointsCommand,
    GGBCenterCommand,
    GGBCircleCommand,
    GGBCircumcircleCommand,
    GGBCommand,
    GGBCompassCommand,
    GGBIntersectCommand,
    GGBLineCommand,
    GGBOrthogonalLineCommand,
    GGBParaCommand,
    GGBReadCommandType,
    GGBTangentOnCircleCommand,
    GGBTangentOutsideCircleCommand,
)
from newclid.ggb.read_elements import GGBConic, GGBLine


def apply_commands_effects_on_elements(
    commands: list[GGBCommand],
    lines: dict[str, GGBLine],
    conics: dict[str, GGBConic],
) -> None:
    for command in commands:
        _apply_command_effect(command, lines, conics)


def _apply_command_effect(
    command: GGBCommand,
    lines: dict[str, GGBLine],
    conics: dict[str, GGBConic],
) -> None:
    match command.construction_type:
        case GGBReadCommandType.Line:
            _add_points_on_line_from_line_command(command, lines)
        case GGBReadCommandType.Intersect:
            _add_points_on_objects_in_intersect_command(command, lines, conics)
        case GGBReadCommandType.OrthogonalLine:
            _add_points_and_line_on_line_from_orthogonal_line_command(command, lines)
        case GGBReadCommandType.ParallelLine:
            _add_points_and_line_on_line_from_parallel_line_command(command, lines)
        case GGBReadCommandType.Circle:
            _add_point_and_center_on_conic_from_circle_command(command, conics)
            _add_radius_from_circle_command(command, conics)
        case GGBReadCommandType.Circumcircle:
            _add_points_on_conic_from_circumcircle_command(command, conics)
        case GGBReadCommandType.Eqdistance:
            _add_point_and_center_from_compass_command(command, conics)
            _add_radius_from_compass_command(command, conics)
        case GGBReadCommandType.AddPointOn:
            _add_point_on_object_command(
                command.point, command.object_name, lines, conics
            )
        case GGBReadCommandType.Center:
            _add_center_to_circle_from_center_command(command, conics)
        case GGBReadCommandType.AngularBisector:
            _add_points_bisecting_lines_from_bisector_command(command, lines)
        case GGBReadCommandType.AngularBisectorPoints:
            _add_bisecting_angles_from_bisector_command(command, lines)
        case GGBReadCommandType.TangentOnCircle:
            _add_tangency_elements_from_tangent_on_circle_command(command, lines)
        case GGBReadCommandType.TangentOutsideCircle:
            _add_tangency_elements_from_tangent_outside_circle_command(command, lines)
        case GGBReadCommandType.AngularBisectorPoints:
            _add_vertex_to_bisector_from_angular_bisector_command(command, lines)
        case _:
            pass


def _add_points_on_line_from_line_command(
    command: GGBLineCommand, lines: dict[str, GGBLine]
) -> None:
    lines[command.line].points.extend([command.point_start, command.point_end])


def _add_points_on_conic_from_circumcircle_command(
    command: GGBCircumcircleCommand, conics: dict[str, GGBConic]
) -> None:
    conics[command.circle].points.extend(
        [command.point_a, command.point_b, command.point_c]
    )


def _add_point_and_center_from_compass_command(
    command: GGBCompassCommand, conics: dict[str, GGBConic]
) -> None:
    conics[command.circle].center = command.center


def _add_radius_from_compass_command(
    command: GGBCompassCommand, conics: dict[str, GGBConic]
) -> None:
    conics[command.circle].radius = command.segment_radius


def _add_points_and_line_on_line_from_orthogonal_line_command(
    command: GGBOrthogonalLineCommand, lines: dict[str, GGBLine]
) -> None:
    lines[command.perpendicular_line].points.append(command.point)


def _add_points_and_line_on_line_from_parallel_line_command(
    command: GGBParaCommand, lines: dict[str, GGBLine]
) -> None:
    lines[command.parallel_line].points.append(command.point_start)


def _add_points_on_objects_in_intersect_command(
    command: GGBIntersectCommand, lines: dict[str, GGBLine], conics: dict[str, GGBConic]
) -> None:
    _add_point_on_object_command(command.point, command.object_1, lines, conics)
    _add_point_on_object_command(command.point, command.object_2, lines, conics)


def _add_point_and_center_on_conic_from_circle_command(
    command: GGBCircleCommand, conics: dict[str, GGBConic]
) -> None:
    conics[command.circle].points.append(command.point_b)
    conics[command.circle].center = command.center


def _add_radius_from_circle_command(
    command: GGBCircleCommand, conics: dict[str, GGBConic]
) -> None:
    conics[command.circle].radius = (command.center, command.point_b)


def _add_point_on_object_command(
    point: str,
    object_name: str,
    lines: dict[str, GGBLine],
    conics: dict[str, GGBConic],
) -> None:
    if object_name in lines:
        lines[object_name].points.append(point)
    elif object_name in conics:
        conics[object_name].points.append(point)


def _add_center_to_circle_from_center_command(
    command: GGBCenterCommand, conics: dict[str, GGBConic]
) -> None:
    conics[command.circle].center = command.point


def _add_points_bisecting_lines_from_bisector_command(
    command: GGBAngularBisectorLinesCommand, lines: dict[str, GGBLine]
) -> None:
    for point in lines[command.line_1].points:
        if point in lines[command.line_2].points:
            lines[command.line_bisector].points.append(point)


def _add_bisecting_angles_from_bisector_command(
    command: GGBAngularBisectorPointsCommand, lines: dict[str, GGBLine]
) -> None:
    lines[command.line_bisector].points.extend(command.corner)


def _add_tangency_elements_from_tangent_on_circle_command(
    command: GGBTangentOnCircleCommand, lines: dict[str, GGBLine]
) -> None:
    lines[command.tangent_line].points.append(command.point_on_tangent)


def _add_vertex_to_bisector_from_angular_bisector_command(
    command: GGBAngularBisectorLinesCommand, lines: dict[str, GGBLine]
) -> None:
    lines[command.line_bisector].points.extend(command.corner)


def _add_tangency_elements_from_tangent_outside_circle_command(
    command: GGBTangentOutsideCircleCommand, lines: dict[str, GGBLine]
) -> None:
    lines[command.tangent_line1].points.append(command.point_on_tangent)
    lines[command.tangent_line2].points.append(command.point_on_tangent)
