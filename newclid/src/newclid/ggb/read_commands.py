from __future__ import annotations

import re
from enum import Enum
from typing import Annotated, Literal
from xml.etree.ElementTree import Element

from pydantic import BaseModel, Field

from newclid.ggb.read_elements import GGBConic, GGBLine, GGBPoint


def read_commands(
    root: Element,
    points: dict[str, GGBPoint],
    lines: dict[str, GGBLine],
    conics: dict[str, GGBConic],
) -> list[GGBCommand]:
    commands: list[GGBCommand] = []
    for xml_command in root.iter("command"):
        command = _read_command(xml_command, points, lines, conics)
        if command is not None:
            commands += command
    return commands


class GGBReadCommandType(Enum):
    Line = "Line"
    OrthogonalLine = "OrthogonalLine"
    Intersect = "Intersect"
    ParallelLine = "ParallelLine"
    Circle = "Circle"
    AddPointOn = "AddPointOn"
    Eqdistance = "Eqdistance"
    Circumcircle = "Circumcircle"
    Segment = "Segment"
    Center = "Center"
    Midpoint = "Midpoint"
    AngularBisector = "AngularBisector"
    AngularBisectorPoints = "AngularBisectorPoints"
    TangentOnCircle = "TangentOnCircle"
    TangentOutsideCircle = "TangentOutsiteCircle"


class GGBLineCommand(BaseModel):
    point_start: str
    point_end: str
    line: str

    construction_type: Literal[GGBReadCommandType.Line] = GGBReadCommandType.Line


class GGBParaCommand(BaseModel):
    point_start: str
    base_line: str
    parallel_line: str

    construction_type: Literal[GGBReadCommandType.ParallelLine] = (
        GGBReadCommandType.ParallelLine
    )


class GGBOrthogonalLineCommand(BaseModel):
    line: str
    point: str
    perpendicular_line: str

    construction_type: Literal[GGBReadCommandType.OrthogonalLine] = (
        GGBReadCommandType.OrthogonalLine
    )


class GGBIntersectCommand(BaseModel):
    object_1: str
    object_2: str
    point: str

    construction_type: Literal[GGBReadCommandType.Intersect] = (
        GGBReadCommandType.Intersect
    )


class GGBCircleCommand(BaseModel):
    center: str
    point_b: str
    circle: str
    construction_type: Literal[GGBReadCommandType.Circle] = GGBReadCommandType.Circle


class GGBCircumcircleCommand(BaseModel):
    point_a: str
    point_b: str
    point_c: str
    circle: str
    construction_type: Literal[GGBReadCommandType.Circumcircle] = (
        GGBReadCommandType.Circumcircle
    )


class GGBCompassCommand(BaseModel):
    center: str
    segment_radius: tuple[str, str]
    circle: str
    construction_type: Literal[GGBReadCommandType.Eqdistance] = (
        GGBReadCommandType.Eqdistance
    )


class GGBAddPointOnObjectCommand(BaseModel):
    object_name: str
    point: str
    construction_type: Literal[GGBReadCommandType.AddPointOn] = (
        GGBReadCommandType.AddPointOn
    )


class GGBCenterCommand(BaseModel):
    circle: str
    point: str
    construction_type: Literal[GGBReadCommandType.Center] = GGBReadCommandType.Center


class GGBMidpointCommand(BaseModel):
    point_a: str
    point_b: str
    midpoint: str
    construction_type: Literal[GGBReadCommandType.Midpoint] = (
        GGBReadCommandType.Midpoint
    )


class GGBAngularBisectorLinesCommand(BaseModel):
    line_1: str
    line_2: str
    line_bisector: str
    construction_type: Literal[GGBReadCommandType.AngularBisector] = (
        GGBReadCommandType.AngularBisector
    )


class GGBAngularBisectorPointsCommand(BaseModel):
    point_a: str
    corner: str
    point_b: str
    line_bisector: str
    construction_type: Literal[GGBReadCommandType.AngularBisectorPoints] = (
        GGBReadCommandType.AngularBisectorPoints
    )


class GGBTangentOnCircleCommand(BaseModel):
    point_on_tangent: str
    tangent_object: str
    tangent_line: str
    construction_type: Literal[GGBReadCommandType.TangentOnCircle] = (
        GGBReadCommandType.TangentOnCircle
    )


class GGBTangentOutsideCircleCommand(BaseModel):
    point_on_tangent: str
    tangent_object: str
    tangent_line1: str
    tangent_line2: str
    construction_type: Literal[GGBReadCommandType.TangentOutsideCircle] = (
        GGBReadCommandType.TangentOutsideCircle
    )


GGBCommand = Annotated[
    GGBOrthogonalLineCommand
    | GGBLineCommand
    | GGBIntersectCommand
    | GGBParaCommand
    | GGBCircleCommand
    | GGBAddPointOnObjectCommand
    | GGBCircumcircleCommand
    | GGBCompassCommand
    | GGBCenterCommand
    | GGBMidpointCommand
    | GGBAngularBisectorLinesCommand
    | GGBTangentOnCircleCommand
    | GGBTangentOutsideCircleCommand
    | GGBAngularBisectorPointsCommand,
    Field(discriminator="construction_type"),
]


class GGBXMLCommandType(Enum):
    Circle = "Circle"
    Center = "Center"
    Line = "Line"
    Segment = "Segment"
    OrthogonalLine = "OrthogonalLine"
    Point = "Point"
    Intersect = "Intersect"
    Midpoint = "Midpoint"
    AngularBisector = "AngularBisector"
    Tangent = "Tangent"


def _read_command(
    command: Element,
    points: dict[str, GGBPoint],
    lines: dict[str, GGBLine],
    conics: dict[str, GGBConic],
) -> list[GGBCommand] | None:
    command_name = GGBXMLCommandType(command.attrib["name"])
    inputs, outputs = list(command)
    match command_name:
        case GGBXMLCommandType.Line:
            return _read_line_xml(inputs, outputs, points, lines)
        case GGBXMLCommandType.OrthogonalLine:
            return [
                GGBOrthogonalLineCommand(
                    point=inputs.attrib["a0"],
                    line=inputs.attrib["a1"],
                    perpendicular_line=outputs.attrib["a0"],
                )
            ]
        case GGBXMLCommandType.Circle:
            return _read_circle_xml(inputs, outputs, points)
        case (
            GGBXMLCommandType.Point
            | GGBXMLCommandType.Intersect
            | GGBXMLCommandType.Center
            | GGBXMLCommandType.Midpoint
        ):
            return _read_point_creation_xml(command_name, inputs, outputs, points)
        case GGBXMLCommandType.AngularBisector:
            return _read_angular_bisector_xml(inputs, outputs, points, lines)
        case GGBXMLCommandType.Tangent:
            return _read_tangent_xml(inputs, outputs, points, lines, conics)
        case GGBXMLCommandType.Segment:
            return None
    raise NotImplementedError(f"Unknown command: {command_name}")


def _read_point_creation_xml(
    command_name: GGBXMLCommandType,
    inputs: Element,
    outputs: Element,
    points: dict[str, GGBPoint],
) -> list[GGBCommand]:
    point_name = outputs.attrib["a0"]
    if point_name not in points:
        # Skip hidden points
        return []
    match command_name:
        case GGBXMLCommandType.Point:
            return [
                GGBAddPointOnObjectCommand(
                    object_name=inputs.attrib["a0"],
                    point=outputs.attrib["a0"],
                )
            ]
        case GGBXMLCommandType.Intersect:
            return [
                GGBIntersectCommand(
                    object_1=inputs.attrib["a0"],
                    object_2=inputs.attrib["a1"],
                    point=outputs.attrib["a0"],
                )
            ]
        case GGBXMLCommandType.Midpoint:
            if outputs.attrib["a0"] in points:
                return [
                    GGBMidpointCommand(
                        point_a=inputs.attrib["a0"],
                        point_b=inputs.attrib["a1"],
                        midpoint=outputs.attrib["a0"],
                    )
                ]
        case GGBXMLCommandType.Center:
            return [
                GGBCenterCommand(
                    circle=inputs.attrib["a0"],
                    point=outputs.attrib["a0"],
                )
            ]
        case _:  # pragma: no cover
            pass
    raise NotImplementedError(f"Unknown point creation command: {command_name}")


def _read_line_xml(
    inputs: Element,
    outputs: Element,
    points: dict[str, GGBPoint],
    lines: dict[str, GGBLine],
) -> list[GGBCommand]:
    point_or_line = inputs.attrib["a1"]
    if point_or_line in points:
        return [
            GGBLineCommand(
                point_start=inputs.attrib["a0"],
                point_end=point_or_line,
                line=outputs.attrib["a0"],
            )
        ]
    if point_or_line in lines:
        return [
            GGBParaCommand(
                point_start=inputs.attrib["a0"],
                base_line=point_or_line,
                parallel_line=outputs.attrib["a0"],
            )
        ]
    raise NotImplementedError(f"Unknown line object: {point_or_line}")


def _read_circle_xml(
    inputs: Element, outputs: Element, points: dict[str, GGBPoint]
) -> list[GGBCommand]:
    point_or_segment = inputs.attrib["a1"]
    if point_or_segment in points:
        if "a2" in inputs.attrib:
            return [
                GGBCircumcircleCommand(
                    point_a=inputs.attrib["a0"],
                    point_b=point_or_segment,
                    point_c=inputs.attrib["a2"],
                    circle=outputs.attrib["a0"],
                )
            ]
        else:
            return [
                GGBCircleCommand(
                    center=inputs.attrib["a0"],
                    point_b=point_or_segment,
                    circle=outputs.attrib["a0"],
                )
            ]
    else:
        radius_extrema_components = _str_to_ggbcommand_components(point_or_segment)
        if len(radius_extrema_components.args) != 2:  # pragma: no cover
            raise ValueError(
                f"Expected 2 arguments for radius extrema, got {radius_extrema_components.args}"
            )
        a, b = radius_extrema_components.args
        return [
            GGBCompassCommand(
                center=inputs.attrib["a0"],
                segment_radius=(a, b),
                circle=outputs.attrib["a0"],
            )
        ]


def _read_angular_bisector_xml(
    inputs: Element,
    outputs: Element,
    points: dict[str, GGBPoint],
    lines: dict[str, GGBLine],
) -> list[GGBCommand]:
    arg_1 = inputs.attrib["a0"]
    if arg_1 in lines:
        return [
            GGBAngularBisectorLinesCommand(
                line_1=arg_1,
                line_2=inputs.attrib["a1"],
                line_bisector=outputs.attrib["a0"],
            ),
            GGBAngularBisectorLinesCommand(
                line_1=arg_1,
                line_2=inputs.attrib["a1"],
                line_bisector=outputs.attrib["a1"],
            ),
        ]
    elif arg_1 in points:
        return [
            GGBAngularBisectorPointsCommand(
                point_a=arg_1,
                corner=inputs.attrib["a1"],
                point_b=inputs.attrib["a2"],
                line_bisector=outputs.attrib["a0"],
            )
        ]
    raise NotImplementedError(f"Unknown angular bisector object: {arg_1}")


def _read_tangent_xml(
    inputs: Element,
    outputs: Element,
    points: dict[str, GGBPoint],
    lines: dict[str, GGBLine],
    conics: dict[str, GGBConic],
) -> list[GGBCommand]:
    arg_1 = inputs.attrib["a0"]
    arg_2 = inputs.attrib["a1"]
    if arg_1 in points and arg_2 in conics:
        if not outputs.attrib["a1"]:
            return [
                GGBTangentOnCircleCommand(
                    point_on_tangent=arg_1,
                    tangent_object=arg_2,
                    tangent_line=outputs.attrib["a0"],
                )
            ]
        else:
            return [
                GGBTangentOutsideCircleCommand(
                    point_on_tangent=arg_1,
                    tangent_object=arg_2,
                    tangent_line1=outputs.attrib["a0"],
                    tangent_line2=outputs.attrib["a1"],
                )
            ]
    raise NotImplementedError("This situation is not handled yet.")


class GGBXMLCommandComponents(BaseModel):
    command_type: str
    args: list[str]


def _str_to_ggbcommand_components(command_str: str) -> GGBXMLCommandComponents:
    split_string = re.match(r"(\w+)\[(.*)\]", command_str)

    if not split_string:  # pragma: no cover
        raise ValueError(f"This may not be a command: '{command_str}'")

    command_type = split_string.group(1)
    command_args = split_string.group(2).split(", ")

    return GGBXMLCommandComponents(command_type=command_type, args=command_args)
