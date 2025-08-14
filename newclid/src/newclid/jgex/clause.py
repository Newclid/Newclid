from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict

from newclid.predicate_types import PredicateArgument
from newclid.tools import atomize, point_construction_tuple


class JGEXConstruction(BaseModel):
    model_config = ConfigDict(frozen=True)

    string: str
    """String representation of the construction."""

    @property
    def name(self) -> str:
        return self.string.split(" ")[0]

    @property
    def args(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(a) for a in self.string.split(" ")[1:])

    @classmethod
    def from_name_and_args(cls, name: str, args: tuple[PredicateArgument, ...]) -> Self:
        return cls.from_tuple((name, *args))

    @classmethod
    def from_str(cls, construction_str: str) -> Self:
        return cls(string=construction_str)

    @classmethod
    def from_tuple(cls, construction_tuple: tuple[str, ...]) -> Self:
        return cls(string=" ".join(construction_tuple))

    def __str__(self) -> str:
        return self.string

    def __hash__(self) -> int:
        return hash(self.string)


def rename_jgex_construction(
    construction: JGEXConstruction,
    mapping: dict[PredicateArgument, PredicateArgument],
) -> JGEXConstruction:
    renamed_args = tuple(mapping.get(arg, arg) for arg in construction.args)
    return JGEXConstruction.from_name_and_args(
        name=construction.name, args=renamed_args
    )


def is_numerical_argument(arg: str) -> bool:
    return not str.isalpha(arg[0])


class JGEXClause(BaseModel):
    model_config = ConfigDict(frozen=True)

    points: tuple[PredicateArgument, ...]
    constructions: tuple[JGEXConstruction, ...]

    def renamed(self, mp: dict[PredicateArgument, PredicateArgument]) -> JGEXClause:
        renamed_constructions: list[JGEXConstruction] = []
        for construction in self.constructions:
            renamed_constructions.append(rename_jgex_construction(construction, mp))
        return JGEXClause(
            points=tuple(mp.get(p, p) for p in self.points),
            constructions=tuple(renamed_constructions),
        )

    @classmethod
    def from_str(cls, s: str) -> tuple[JGEXClause, ...]:
        chunks = atomize(s, ";")

        clauses: list[JGEXClause] = []
        for chunk in chunks:
            points: tuple[PredicateArgument, ...] = tuple()
            points_str, construction_str = (
                chunk.split(":")
                if ":" in chunk
                else chunk.split("=")
                if "=" in chunk
                else ("", chunk)
            )
            points = tuple(PredicateArgument(p) for p in points_str.strip().split())
            construction_str = construction_str.strip()
            construction_tuples = tuple(
                atomize(b) for b in construction_str.split(",") if b.strip() != ""
            )
            clauses.append(
                JGEXClause(
                    points=points,
                    constructions=tuple(
                        JGEXConstruction.from_tuple(construction_tuple)
                        for construction_tuple in construction_tuples
                    ),
                )
            )
        return tuple(clauses)

    def __hash__(self) -> int:
        return hash((self.points, *self.constructions))

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{' '.join(p for p in self.points)} = {', '.join(str(c) for c in self.constructions)}"


def order_clauses_by_points_construction_order(
    clauses: list[JGEXClause],
) -> list[JGEXClause]:
    """Order the clauses by the construction order of the points in the clause."""
    return sorted(
        clauses,
        key=lambda clause: min(point_construction_tuple(p) for p in clause.points),
    )
