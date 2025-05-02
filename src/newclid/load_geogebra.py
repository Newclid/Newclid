from enum import Enum
import logging
from pathlib import Path
import re
from typing import Optional
from zipfile import ZipFile
from xml.etree.ElementTree import parse
from collections import defaultdict
from newclid.dependencies.dependency import IN_PREMISES, Dependency
from newclid.numerical.geometries import PointNum
from newclid.predicates.circumcenter import Circumcenter
from newclid.predicates.collinearity import Coll
from newclid.predicates.congruence import Cong
from newclid.predicates.cyclic import Cyclic
from newclid.predicates.midpoint import MidPoint
from newclid.predicates.perpendicularity import Perp

from newclid.dependencies.dependency_graph import DependencyGraph
from newclid.statement import Statement

LOGGER = logging.getLogger(__name__)


class Form(Enum):
    Circle = 0
    Line = 1


def dedup(t: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(obj for k, obj in enumerate(t) if obj not in t[:k])


def load_geogebra(path: Path, dep_graph: DependencyGraph):
    ggb = ZipFile(path, "r").open("geogebra.xml")
    tree = parse(ggb)
    root = tree.getroot()
    symbols_graph = dep_graph.symbols_graph
    for e in root.iter("element"):
        if e.attrib["type"] == "point":
            (p,) = symbols_graph.names2points([e.attrib["label"]])
            (coords,) = e.iter("coords")
            x, y, z = map(
                float, (coords.attrib["x"], coords.attrib["y"], coords.attrib["z"])
            )
            p.num = PointNum(x / z, y / z)
            LOGGER.info(f"Find coordinates of {p} ({p.num})")
    # associating points with forms
    # points in a form
    ensemble: dict[str, tuple[str, ...]] = defaultdict(lambda: ())
    # which form is it
    form: dict[str, Form] = {}
    # auxilliary data
    aux: dict[str, tuple[str, ...]] = {}
    for command in root.iter("command"):
        command_name = command.attrib["name"]
        (input,) = command.iter("input")
        input_len = 0
        while "a" + str(input_len) in input.attrib:
            input_len += 1

        def a(k: int):
            """
            get the k-th attribute
            """
            return input.attrib["a" + str(k)]

        output = list(command.iter("output"))[0].attrib["a0"]
        if command_name == "Circle":
            if input_len == 2:
                match = re.match(r"Segment\[(.*?),\s*(.*?)\]", a(1))
                if match:
                    x = match.group(1).strip()
                    y = match.group(2).strip()
                    aux[output] = (a(0), x, y)
                else:
                    ensemble[output] += (a(1),)
                    aux[output] = (a(0),)
            else:
                ensemble[output] += (a(0), a(1), a(2))
            form[output] = Form.Circle
        if command_name == "Center":
            aux[a(0)] = (output,)
            form[output] = Form.Circle
        elif command_name == "Line" or command_name == "Segment":
            ensemble[output] += (a(0), a(1))
            form[output] = Form.Line
        elif command_name == "OrthogonalLine":
            ensemble[output] += (a(0),)
            form[output] = Form.Line
        elif command_name == "Point":
            ensemble[a(0)] += (output,)
        elif command_name == "Intersect":
            ensemble[a(0)] += (output,)
            ensemble[a(1)] += (output,)
    # add premises
    premises: list[Optional[Statement]] = []
    for k, points in ensemble.items():
        points = dedup(points)
        if form[k] == Form.Circle:
            if k in aux:
                t = aux[k]
                if len(t) == 1:
                    premises.append(
                        Statement.from_tokens(
                            (Circumcenter.NAME, t[0]) + points, dep_graph
                        )
                    )
                else:
                    premises.append(
                        Statement.from_tokens(
                            (Circumcenter.NAME, t[0]) + points, dep_graph
                        )
                    )
                    premises.append(
                        Statement.from_tokens(
                            (Cong.NAME, t[1], t[2], t[0], points[0]), dep_graph
                        )
                    )
            premises.append(Statement.from_tokens((Cyclic.NAME,) + points, dep_graph))
        if form[k] == Form.Line:
            premises.append(Statement.from_tokens((Coll.NAME,) + points, dep_graph))

    for command in root.iter("command"):
        command_name = command.attrib["name"]
        (input,) = command.iter("input")
        input_len = 0
        while "a" + str(input_len + 1) in input.attrib:
            input_len += 1

        def a(k: int):
            return input.attrib["a" + str(k)]

        output = list(command.iter("output"))[0].attrib["a0"]
        command_name = command.attrib["name"]
        if command_name == "OrthogonalLine":
            # PerpendicularLine(B, f)
            x, y, *_ = ensemble[a(1)]
            u, v, *_ = ensemble[output]
            premises.append(Statement.from_tokens((Perp.NAME, x, y, u, v), dep_graph))
        elif command_name == "Mirror":
            premises.append(
                Statement.from_tokens((MidPoint.NAME, a(1), a(0), output), dep_graph)
            )

    for statement in premises:
        if statement:
            Dependency.mk(statement, IN_PREMISES, ()).add()
