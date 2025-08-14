import logging
from pathlib import Path
from typing import Self

from numpy.random import Generator as RngGenerator

from newclid.api import ProblemBuilder
from newclid.jgex.clause import JGEXClause
from newclid.jgex.constructions import ALL_JGEX_CONSTRUCTIONS
from newclid.jgex.definition import JGEXDefinition
from newclid.jgex.errors import JGEXConstructionError
from newclid.jgex.formulation import (
    JGEXFormulation,
    alphabetize,
    jgex_formulation_from_txt_file,
)
from newclid.jgex.to_newclid import JGEXClauseConsequences, build_newclid_problem
from newclid.problem import ProblemSetup, nc_problem_is_valid
from newclid.rng import setup_rng

LOGGER = logging.getLogger(__name__)


class JGEXProblemBuilder(ProblemBuilder):
    def __init__(
        self,
        rng: RngGenerator | int | None = None,
        problem: JGEXFormulation | None = None,
        max_attempts_per_clause: int = 5,
    ) -> None:
        self.jgex_problem = problem
        self.rng = setup_rng(rng)
        self.max_attempts_per_clause = max_attempts_per_clause
        self.jgex_defs: dict[str, JGEXDefinition] = JGEXDefinition.to_dict(
            ALL_JGEX_CONSTRUCTIONS
        )
        self._clauses_consequences: dict[JGEXClause, JGEXClauseConsequences] | None = (
            None
        )
        self._include_auxiliary_clauses: bool = False

    def build(
        self, max_attempts_to_satisfy_goals_numerically: int = 100
    ) -> ProblemSetup:
        if self.jgex_problem is None:
            raise ValueError("JGEX problem is not set by any means.")

        valid_problem_setup = None
        last_error = JGEXConstructionError(
            f"Did not even try to build a valid problem setup for {self.jgex_problem.name}."
        )
        for _attempt in range(max_attempts_to_satisfy_goals_numerically):
            try:
                problem_setup, clauses_consequences = build_newclid_problem(
                    problem=self.jgex_problem,
                    defs=self.jgex_defs,
                    max_attempts_per_clause=self.max_attempts_per_clause,
                    rng=self.rng,
                    include_auxiliary_clauses=self._include_auxiliary_clauses,
                )
                if nc_problem_is_valid(problem_setup):
                    valid_problem_setup = problem_setup
                    self._clauses_consequences = clauses_consequences
                    break
            except JGEXConstructionError as e:
                LOGGER.debug(
                    f"Failed to build a valid problem setup (attempt {_attempt}): {e}"
                )
                last_error = e
                continue

        if valid_problem_setup is None:
            raise ValueError(
                f"Failed to build a valid problem setup for {self.jgex_problem.name} after {max_attempts_to_satisfy_goals_numerically} attempts. Last error: {last_error}"
            ) from last_error

        return valid_problem_setup

    def with_problem(self, problem: JGEXFormulation) -> Self:
        self.jgex_problem = problem
        return self

    def with_problem_from_txt(
        self, problem_txt: str, problem_name: str = "problem"
    ) -> Self:
        self.jgex_problem = JGEXFormulation.from_text(problem_txt)
        self.jgex_problem.name = problem_name
        return self

    def include_auxiliary_clauses(self, include: bool = True) -> Self:
        self._include_auxiliary_clauses = include
        return self

    def with_problem_from_file(
        self, problems_path: Path, problem_name: str, rename: bool = False
    ) -> Self:
        problems = jgex_formulation_from_txt_file(problems_path)
        try:
            self.jgex_problem = problems[problem_name]
        except KeyError as e:
            raise KeyError(f"{problem_name} not found in file {problems_path}") from e
        if rename:
            self.jgex_problem, _reversed_mapping = alphabetize(self.jgex_problem)
        return self

    def with_defs(self, defs: list[JGEXDefinition]) -> Self:
        self.jgex_defs = JGEXDefinition.to_dict(defs)
        return self

    @property
    def clauses_consequences(self) -> dict[JGEXClause, JGEXClauseConsequences]:
        if self._clauses_consequences is None:
            raise ValueError(
                "JGEX clauses consequences are not set."
                " You need to build first to use this property."
            )
        return self._clauses_consequences
