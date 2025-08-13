"""Define the problem setup taken as input by Newclid."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, field_validator, model_validator

from newclid.predicate_types import PredicateArgument
from newclid.predicates import (
    Predicate,
    predicate_class_from_type,
    predicate_from_construction,
)
from newclid.predicates._index import PredicateType
from newclid.symbols.points_registry import Point, PointsRegisty
from newclid.tools import point_construction_tuple

SEPARATOR = " "


class PredicateConstruction(BaseModel):
    string: str
    """String representation of the construction."""

    @property
    def predicate_type(self) -> PredicateType:
        return PredicateType(self.string.split(SEPARATOR)[0])

    @property
    def args(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(a) for a in self.string.split(SEPARATOR)[1:])

    @model_validator(mode="after")
    def canonicalize(self) -> Self:
        predicate_class = predicate_class_from_type(self.predicate_type)
        parsed_args = predicate_class.preparse(
            tuple(PredicateArgument(a) for a in self.args)
        )
        if parsed_args is None:
            raise ValueError(f"Invalid construction: {self}")
        self.string = SEPARATOR.join(
            (self.predicate_type.value, *tuple(str(a) for a in parsed_args))
        )
        return self

    @classmethod
    def from_tuple(cls, construction_tuple: tuple[str, ...]) -> PredicateConstruction:
        return cls(string=SEPARATOR.join(construction_tuple))

    @classmethod
    def from_str(cls, construction_str: str) -> PredicateConstruction:
        return cls(string=construction_str)

    @classmethod
    def from_predicate_type_and_args(
        cls, predicate_type: PredicateType, args: tuple[PredicateArgument, ...]
    ) -> PredicateConstruction:
        return cls.from_tuple((predicate_type.value, *args))

    def __str__(self) -> str:
        return self.string

    def __repr__(self) -> str:
        return self.string

    def __hash__(self) -> int:
        return hash(self.string)


def predicate_from_str(predicate_str: str, points: PointsRegisty) -> Predicate:
    construction = PredicateConstruction.from_str(predicate_str)
    predicate = predicate_from_construction(construction, points)
    if predicate is None:
        raise ValueError(f"Invalid predicate string: {predicate_str}")
    return predicate


def predicate_to_construction(predicate: Predicate) -> PredicateConstruction:
    return PredicateConstruction.from_predicate_type_and_args(
        predicate_type=predicate.predicate_type, args=predicate.to_tokens()
    )


def is_numerical_argument(arg: str) -> bool:
    return not str.isalpha(arg[0])


def predicate_points(predicate: Predicate) -> set[PredicateArgument]:
    construction = predicate_to_construction(predicate)
    return {pname for pname in construction.args if not is_numerical_argument(pname)}


def rename_predicate_construction(
    predicate_construction: PredicateConstruction,
    mapping: dict[PredicateArgument, PredicateArgument],
) -> PredicateConstruction:
    """Rename the points in a predicate construction."""
    return PredicateConstruction.from_tuple(
        (
            predicate_construction.predicate_type.value,
            *tuple(mapping.get(arg, arg) for arg in predicate_construction.args),
        )
    )


class ProblemSetup(BaseModel):
    name: str = "problem"
    points: tuple[Point, ...]
    assumptions: tuple[PredicateConstruction, ...]
    goals: tuple[PredicateConstruction, ...]

    @field_validator("points")
    def check_points_are_unique(cls, v: tuple[Point, ...]) -> tuple[Point, ...]:
        if len(v) != len(set(p.name for p in v)):
            raise ValueError("Points must be unique")
        return v

    @model_validator(mode="after")
    def check_assumptions_and_goals_refer_to_existing_points(self) -> Self:
        point_names = {p.name for p in self.points}
        for construction in self.assumptions + self.goals:
            for arg in construction.args:
                if str.isalpha(arg[0]) and arg not in point_names:
                    raise ValueError(
                        f"Construction {construction} refers to non-existing point {arg}"
                    )
        self.points = tuple(
            sorted(self.points, key=lambda p: point_construction_tuple(p.name))
        )
        self.assumptions = tuple(sorted(self.assumptions, key=str))
        self.goals = tuple(sorted(self.goals, key=str))
        return self

    def with_new(
        self,
        *,
        new_points: tuple[Point, ...] = (),
        new_assumptions: tuple[PredicateConstruction, ...] = (),
        new_goals: tuple[PredicateConstruction, ...] = (),
    ) -> ProblemSetup:
        return ProblemSetup(
            points=self.points + new_points,
            assumptions=self.assumptions + new_assumptions,
            goals=self.goals + new_goals,
        )

    def pretty_str(self) -> str:
        result = f"Built the problem {self.name} with assumptions:\n"
        for assumption in self.assumptions:
            result += f"{assumption}\n"
        result += "\nand goals:\n"
        for goal in self.goals:
            result += f"{goal}\n"

        result += "\nUsing points:\n"
        for point in self.points:
            result += f"{point.name} ({point.num.x}, {point.num.y})\n"
        return result


def nc_problem_is_valid(problem: ProblemSetup) -> bool:
    """Check if a problem is valid."""
    points_registry = PointsRegisty()
    for point in problem.points:
        points_registry.add_point(point)
    for predicate_construction in problem.assumptions + problem.goals:
        if not _predicate_construction_is_valid(
            predicate_construction, points_registry
        ):
            return False
    return True


def _predicate_construction_is_valid(
    predicate_construction: PredicateConstruction,
    points_registry: PointsRegisty,
) -> bool:
    """Check if a predicate is valid."""
    predicate = predicate_from_construction(predicate_construction, points_registry)
    return predicate is not None and predicate.check_numerical()


def rename_points_in_nc_problem(
    nc_problem: ProblemSetup, mapping: dict[PredicateArgument, PredicateArgument]
) -> ProblemSetup:
    """Rename the points in the problem and the apply the change to the assumptions and goals.

    Points not present in the mapping will be ignored.
    """
    existing_points = {p.name for p in nc_problem.points}
    for old_name in mapping.keys():
        if old_name not in existing_points:
            raise ValueError(f"Point {old_name} does not exist and yet is mapped.")

    renamed_points = tuple(
        Point(name=mapping.get(p.name, p.name), num=p.num) for p in nc_problem.points
    )
    renamed_assumptions = tuple(
        rename_predicate_construction(a, mapping) for a in nc_problem.assumptions
    )
    renamed_goals = tuple(
        rename_predicate_construction(g, mapping) for g in nc_problem.goals
    )
    return ProblemSetup(
        points=renamed_points, assumptions=renamed_assumptions, goals=renamed_goals
    )


def filter_points_from_nc_problem(
    nc_problem: ProblemSetup, points_to_keep: list[PredicateArgument]
) -> ProblemSetup:
    """Filter the points in the problem and remove the assumptions and goals that refer to unkept points."""
    if len(points_to_keep) == 0:
        raise ValueError(
            "There is no point to keep, create a new problem instead if this is expected."
        )

    points_kept_names = set(
        p.name for p in nc_problem.points if p.name in points_to_keep
    )
    if len(points_kept_names) != len(points_to_keep):
        raise ValueError("Some points to keep do not exist in the problem.")

    points_kept = tuple(p for p in nc_problem.points if p.name in points_kept_names)
    assumptions_kept = tuple(
        a
        for a in nc_problem.assumptions
        if all(arg in points_kept_names for arg in a.args)
    )
    goals_kept = tuple(
        g for g in nc_problem.goals if all(arg in points_kept_names for arg in g.args)
    )
    return ProblemSetup(
        points=points_kept, assumptions=assumptions_kept, goals=goals_kept
    )
