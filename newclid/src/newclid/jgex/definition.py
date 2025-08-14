from __future__ import annotations

from typing import NewType

from pydantic import BaseModel

from newclid.jgex.clause import JGEXClause, JGEXConstruction
from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.predicate_types import PredicateArgument
from newclid.tools import atomize

JGEXVariableName = NewType("JGEXVariableName", str)


class SketchConstruction(BaseModel):
    name: str  # TODO: have an enum / union type instead of generic str for all the possible sketches != jgex defs
    args: tuple[JGEXVariableName, ...]

    @classmethod
    def from_str(cls, s: str) -> SketchConstruction:
        name, *args = atomize(s)
        return cls(name=name, args=tuple(JGEXVariableName(a) for a in args))


class SketchCall(BaseModel):
    name: str
    args: tuple[PredicateArgument, ...]

    @classmethod
    def from_construction(
        cls,
        construction: SketchConstruction,
        mapping: dict[JGEXVariableName, PredicateArgument],
    ) -> SketchCall:
        return cls(
            name=construction.name,
            args=tuple(mapping[arg] for arg in construction.args),
        )


def v(s: str) -> JGEXVariableName:
    return JGEXVariableName(s)


class JGEXDefinition(BaseModel):
    """Definitions of construction predicates."""

    name: JGEXConstructionName
    args: tuple[JGEXVariableName, ...]
    rely_on_points: dict[JGEXVariableName, tuple[JGEXVariableName, ...]]
    requirements: JGEXClause
    clauses: tuple[JGEXClause, ...]
    sketches: tuple[SketchConstruction, ...]
    input_points: tuple[JGEXVariableName, ...] = ()
    output_points: tuple[JGEXVariableName, ...] = ()

    @staticmethod
    def to_dict(
        defs: list[JGEXDefinition],
    ) -> dict[str, JGEXDefinition]:
        return {d.name.value: d for d in defs}


def mapping_from_construction(
    construction: JGEXConstruction,
    construction_definition: JGEXDefinition,
) -> dict[JGEXVariableName, PredicateArgument]:
    if not len(construction.args) == len(construction_definition.args):
        raise ValueError(
            f"Construction {construction} has {len(construction.args)}"
            f" arguments but definition {construction_definition.name}"
            f" has {len(construction_definition.args)}"
        )
    mapping = dict(zip(construction_definition.args, construction.args))
    return mapping


def input_points_of_clause(
    clause: JGEXClause, defs: dict[JGEXConstructionName, JGEXDefinition]
) -> set[PredicateArgument]:
    """Get the input points of a clause."""
    input_points: set[PredicateArgument] = set()
    for construction in clause.constructions:
        cdef = defs[JGEXConstructionName(construction.name)]
        mapping = mapping_from_construction(construction, cdef)
        mapped_inputs = {mapping[p] for p in cdef.input_points}
        input_points.update(mapped_inputs)
    return input_points
