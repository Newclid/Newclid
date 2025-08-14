"""Implements objects to represent problems, theorems, proofs, traceback."""

from __future__ import annotations

import string
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from newclid.jgex.clause import JGEXClause
from newclid.predicate_types import PredicateArgument
from newclid.problem import PredicateConstruction, rename_predicate_construction
from newclid.tools import atomize, points_by_construction_order, reshape

ALPHABET: list[str] = (
    list(string.ascii_lowercase)
    + [c + "1" for c in string.ascii_lowercase]
    + [c + "2" for c in string.ascii_lowercase]
    + [c + "3" for c in string.ascii_lowercase]
    + [c + "4" for c in string.ascii_lowercase]
    + [c + "5" for c in string.ascii_lowercase]
    + [c + "6" for c in string.ascii_lowercase]
)

CLAUSES_SEPARATOR = "; "
AUX_SEPARATOR = " | "
GOAL_SEPARATOR = " ? "
MULTI_GOALS_SEPARATOR = "; "


class JGEXFormulation(BaseModel):
    """Describe one problem to solve."""

    name: str = "ProblemJGEX"
    setup_clauses: tuple[JGEXClause, ...]
    auxiliary_clauses: tuple[JGEXClause, ...] = ()
    goals: tuple[PredicateConstruction, ...]

    formulation_type: Literal["jgex"] = "jgex"

    @property
    def clauses(self) -> tuple[JGEXClause, ...]:
        return self.setup_clauses + self.auxiliary_clauses

    @classmethod
    def from_text(cls, text: str) -> JGEXFormulation:
        """Load a problem from a string."""
        name = ""
        if "\n" in text:
            name, text = text.split("\n")

        if GOAL_SEPARATOR in text:
            constructions_str, goals_str = atomize(text, GOAL_SEPARATOR)
        else:
            constructions_str, goals_str = text, ""
        goals_strs = atomize(goals_str, MULTI_GOALS_SEPARATOR)
        goals: tuple[PredicateConstruction, ...] = tuple()
        if len(goals_strs) > 0:
            goals = tuple(PredicateConstruction.from_str(g) for g in goals_strs if g)

        if AUX_SEPARATOR in constructions_str:
            setup_str, aux_str = atomize(constructions_str, AUX_SEPARATOR)
            auxiliary_clauses = JGEXClause.from_str(aux_str)
        else:
            setup_str, aux_str = constructions_str, ""
            auxiliary_clauses = ()

        setup_clauses = JGEXClause.from_str(setup_str)
        return cls(
            name=name,
            setup_clauses=setup_clauses,
            auxiliary_clauses=auxiliary_clauses,
            goals=goals,
        )

    @property
    def points(self) -> tuple[PredicateArgument, ...]:
        s: set[PredicateArgument] = set()
        for construction in self.clauses:
            s.update(construction.points)
        return tuple(points_by_construction_order(s))

    def renamed(
        self, mapping: dict[PredicateArgument, PredicateArgument]
    ) -> JGEXFormulation:
        renamed_setup_clauses = tuple(
            clause.renamed(mapping) for clause in self.setup_clauses
        )
        renamed_aux_clauses = tuple(
            clause.renamed(mapping) for clause in self.auxiliary_clauses
        )
        renamed_goals = tuple(
            rename_predicate_construction(goal, mapping) for goal in self.goals
        )
        return JGEXFormulation(
            name=self.name,
            setup_clauses=renamed_setup_clauses,
            auxiliary_clauses=renamed_aux_clauses,
            goals=renamed_goals,
        )

    def __str__(self) -> str:
        setup_str = CLAUSES_SEPARATOR.join(str(c) for c in self.setup_clauses)
        goals_str = MULTI_GOALS_SEPARATOR.join(str(goal) for goal in self.goals)
        aux_str = ""
        if self.auxiliary_clauses:
            aux_str = AUX_SEPARATOR + CLAUSES_SEPARATOR.join(
                str(c) for c in self.auxiliary_clauses
            )
        return setup_str + aux_str + GOAL_SEPARATOR + goals_str

    def __hash__(self) -> int:
        return hash(str(self))


def jgex_formulation_from_txt_file(fname: Path) -> dict[str, JGEXFormulation]:
    with open(fname, "r") as f:
        lines = f.read().split("\n")

    lines = [line for line in lines if line and not line.startswith("#")]
    problems = [
        JGEXFormulation.from_text(url + "\n" + problem)
        for (url, problem) in reshape(lines, 2)
    ]
    return {p.name: p for p in problems}


def alphabetize(
    problem: JGEXFormulation,
) -> tuple[JGEXFormulation, dict[PredicateArgument, PredicateArgument]]:
    """Alphabetize the problem by renaming the points such that the points are in alphabetical order by construction order.

    Returns the renamed problem and the mapping from the alphabetized points to the original points.
    """
    original_to_alphabetized: dict[PredicateArgument, PredicateArgument] = {}

    renamed_setup_clauses = _alphabetize_clauses(
        problem.setup_clauses, original_to_alphabetized
    )
    renamed_aux_clauses = _alphabetize_clauses(
        problem.auxiliary_clauses, original_to_alphabetized
    )

    renamed_goals = tuple(
        rename_predicate_construction(goal_construction, original_to_alphabetized)
        for goal_construction in problem.goals
    )
    renamed_problem = JGEXFormulation(
        name=problem.name,
        setup_clauses=renamed_setup_clauses,
        auxiliary_clauses=renamed_aux_clauses,
        goals=renamed_goals,
    )
    alphabetized_to_original = {v: k for k, v in original_to_alphabetized.items()}
    return renamed_problem, alphabetized_to_original


def _alphabetize_clauses(
    clauses: tuple[JGEXClause, ...], mapping: dict[PredicateArgument, PredicateArgument]
) -> tuple[JGEXClause, ...]:
    for construction in clauses:
        for point in construction.points:
            if point in mapping:
                continue
            mapping[point] = PredicateArgument(ALPHABET[len(mapping)])
    return tuple(construction.renamed(mapping) for construction in clauses)
