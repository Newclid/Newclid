from enum import Enum
from typing import Annotated, Literal
from xml.etree.ElementTree import Element

from pydantic import BaseModel, Field

from newclid.numerical.geometries import PointNum
from newclid.predicate_types import PredicateArgument
from newclid.symbols.points_registry import Point


class GGBElementType(Enum):
    POINT = "point"
    LINE = "line"
    CONIC = "conic"
    SEGMENT = "segment"


class GGBPoint(BaseModel):
    type: Literal[GGBElementType.POINT] = GGBElementType.POINT
    label: str
    x: float
    y: float
    z: float

    @classmethod
    def from_xml_element(cls, element: Element) -> "GGBPoint":
        (coords,) = element.iter("coords")
        x, y, z = map(
            float, (coords.attrib["x"], coords.attrib["y"], coords.attrib["z"])
        )
        return cls(label=element.attrib["label"], x=x, y=y, z=z)

    def to_newclid(self) -> Point:
        return Point(
            name=PredicateArgument(self.label),
            num=PointNum(x=self.x / self.z, y=self.y / self.z),
        )


class GGBLine(BaseModel):
    type: Literal[GGBElementType.LINE] = GGBElementType.LINE
    line_name: str
    points: list[str] = []

    @classmethod
    def from_xml_element(cls, element: Element) -> "GGBLine":
        return cls(line_name=element.attrib["label"])


class GGBConic(BaseModel):
    type: Literal[GGBElementType.CONIC] = GGBElementType.CONIC
    conic_name: str
    points: list[str] = []
    center: str | None = None
    radius: str | tuple[str, str] | None = None

    @classmethod
    def from_xml_element(cls, element: Element) -> "GGBConic":
        return cls(conic_name=element.attrib["label"])


GGBElement = Annotated[GGBLine | GGBPoint | GGBConic, Field(discriminator="type")]


def read_elements(
    root: Element,
) -> tuple[dict[str, GGBPoint], dict[str, GGBLine], dict[str, GGBConic]]:
    points: dict[str, GGBPoint] = {}
    lines: dict[str, GGBLine] = {}
    conics: dict[str, GGBConic] = {}
    for e in root.iter("element"):
        match GGBElementType(e.attrib["type"]):
            case GGBElementType.POINT:
                show = e.find("show")
                if show is not None and show.attrib["object"] == "true":
                    point = GGBPoint.from_xml_element(e)
                    points[point.label] = point
            case GGBElementType.LINE:
                line = GGBLine.from_xml_element(e)
                lines[line.line_name] = line
            case GGBElementType.CONIC:
                conic = GGBConic.from_xml_element(e)
                conics[conic.conic_name] = conic
            case GGBElementType.SEGMENT:
                pass  # TODO: handle segments or do they have line already?

    return points, lines, conics
