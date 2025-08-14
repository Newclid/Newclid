import logging
from pathlib import Path
from typing import Self
from xml.etree.ElementTree import parse
from zipfile import ZipFile

from pydantic import BaseModel

from newclid.api import ProblemBuilder
from newclid.ggb.apply_commands_effects import apply_commands_effects_on_elements
from newclid.ggb.assumptions_from_commands import commands_to_newclid_assumptions
from newclid.ggb.assumptions_from_elements import elements_to_newclid_assumptions
from newclid.ggb.assumptions_from_elements_relation import (
    relationships_to_newclid_assumptions,
)
from newclid.ggb.elements_relationships import ElementsRelationships
from newclid.ggb.read_commands import GGBCommand, read_commands
from newclid.ggb.read_elements import GGBConic, GGBLine, GGBPoint, read_elements
from newclid.ggb.relationships_from_commands import relationships_from_commands
from newclid.problem import PredicateConstruction, ProblemSetup
from newclid.symbols.points_registry import Point

LOGGER = logging.getLogger(__name__)


class GeogebraProblemBuilder(ProblemBuilder):
    def __init__(self, ggb_file_path: Path):
        self.ggb_file_path = ggb_file_path
        self.problem_name: str = "GeogebraProblem"
        self.goals: list[PredicateConstruction] = []
        self.removed_assumptions: list[PredicateConstruction] = []
        self.extra_assumptions: list[PredicateConstruction] = []

    def with_goals(self, goals: list[PredicateConstruction]) -> Self:
        self.goals.extend(goals)
        return self

    def without_assumptions(self, assumptions: list[PredicateConstruction]) -> Self:
        self.removed_assumptions.extend(assumptions)
        return self

    def with_extra_assumptions(self, assumptions: list[PredicateConstruction]) -> Self:
        self.extra_assumptions.extend(assumptions)
        return self

    def build(self) -> ProblemSetup:
        problem_name = self.ggb_file_path.name.removesuffix(".ggb")
        points, assumptions = load_ggb_file(self.ggb_file_path)
        assumptions.extend(self.extra_assumptions)
        assumptions = [a for a in assumptions if a not in self.removed_assumptions]
        problem = ProblemSetup(
            name=problem_name,
            goals=tuple(self.goals),
            points=tuple(points),
            assumptions=tuple(assumptions),
        )
        LOGGER.info(
            f"Loaded problem ’{problem.name}’ with {len(points)} points"
            f" and {len(assumptions)} assumptions from GeoGebra."
        )
        return problem


def load_ggb_file(
    ggb_file_path: Path,
) -> tuple[list[Point], list[PredicateConstruction]]:
    ggbsetup = _load_geogebra_setup(ggb_file_path)

    points = [p.to_newclid() for p in ggbsetup.points.values()]

    assumptions: list[PredicateConstruction] = []
    assumptions.extend(
        commands_to_newclid_assumptions(
            ggbsetup.commands, ggbsetup.lines, ggbsetup.conics
        )
    )
    assumptions.extend(elements_to_newclid_assumptions(ggbsetup.lines, ggbsetup.conics))
    assumptions.extend(relationships_to_newclid_assumptions(ggbsetup.relationships))
    points.sort(key=lambda p: p.name)
    deduping_assumptions = set(assumptions)
    assumptions = list(deduping_assumptions)
    return points, assumptions


class GGBSetup(BaseModel):
    points: dict[str, GGBPoint]
    lines: dict[str, GGBLine]
    conics: dict[str, GGBConic]
    commands: list[GGBCommand]
    relationships: list[ElementsRelationships]


def _load_geogebra_setup(ggb_file_path: Path) -> GGBSetup:
    LOGGER.debug(f"Loading GeoGebra file at {ggb_file_path}")
    with ZipFile(ggb_file_path, "r").open("geogebra.xml") as ggb:
        tree = parse(ggb)
    root = tree.getroot()
    points, lines, conics = read_elements(root)
    points_str = "\n" + "\n".join(
        pt.model_dump_json(indent=2) for pt in points.values()
    )
    lines_str = "\n" + "\n".join(
        line.model_dump_json(indent=2) for line in lines.values()
    )
    conics_str = "\n" + "\n".join(
        conic.model_dump_json(indent=2) for conic in conics.values()
    )
    LOGGER.debug(
        f"GGB Elements:\nPoints: {points_str}\nLines: {lines_str}\nConics: {conics_str}"
    )

    commands = read_commands(root, points, lines, conics)
    commands_str = "\n" + "\n".join(c.model_dump_json(indent=2) for c in commands)
    LOGGER.debug(f"GGB Commands: {commands_str}")
    apply_commands_effects_on_elements(commands, lines, conics)
    relationships = relationships_from_commands(commands, points, lines, conics)
    return GGBSetup(
        points=points,
        lines=lines,
        conics=conics,
        commands=commands,
        relationships=relationships,
    )
