"""Module to convert problems to and from LLM input."""

from __future__ import annotations

import re
from typing import Self

import numpy as np
from pydantic import BaseModel

from newclid.api import GeometricSolverBuilder
from newclid.jgex.clause import JGEXClause, JGEXConstruction
from newclid.jgex.formulation import JGEXFormulation
from newclid.jgex.jgex_setup_data import (
    JGEXClauseInProof,
    JGEXSetupData,
    PredicateConstructionInSetup,
    jgex_clauses_to_setup_data,
)
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.justifications._index import JustificationType
from newclid.predicate_types import PredicateArgument
from newclid.problem import PredicateConstruction, predicate_to_construction
from newclid.proof_data import PredicateInProof, ProofData, ProofStep


def new_problem_from_llm_aux_output(
    initial_problem: JGEXFormulation, aux_output: str, aux_tag: str
) -> JGEXFormulation:
    sanitized_aux_output = _clauses_in_aux_output(aux_output, aux_tag)
    aux_clauses = tuple(_llm_str_to_clause(c) for c in sanitized_aux_output)
    problem_with_aux = JGEXFormulation(
        name=initial_problem.name + "_with_" + aux_output,
        setup_clauses=initial_problem.setup_clauses,
        auxiliary_clauses=aux_clauses,
        goals=initial_problem.goals,
    )
    return problem_with_aux


def problem_to_llm_input(
    problem: JGEXFormulation,
    aux_tag: str,
    rng: np.random.Generator | None = None,
    max_attempts: int = 200,
) -> str:
    """
    Convert a problem to a string that can be used as input for the LLM.

    Args:
        problem: The problem to convert.
        aux_tag: The tag to use for the aux clauses.
        rng: The random number generator to use.
        max_attempts: The maximum number of attempts to make for building the problem.
    """
    formulation_with_aux_in_setup = JGEXFormulation(
        name=problem.name,
        setup_clauses=problem.setup_clauses + problem.auxiliary_clauses,
        auxiliary_clauses=(),
        goals=problem.goals,
    )
    setup_data = _problem_jgex_to_setup_data(
        formulation_with_aux_in_setup, rng=rng, max_attempts=max_attempts
    )
    training_data = AuxTrainingDatapoint.from_setup_data(setup_data, aux_tag)
    return training_data.input


def problem_to_llm_input_without_predicates(problem: JGEXFormulation) -> str:
    formulation_with_aux_in_setup = JGEXFormulation(
        name=problem.name,
        setup_clauses=problem.setup_clauses + problem.auxiliary_clauses,
        auxiliary_clauses=(),
        goals=problem.goals,
    )
    return str(formulation_with_aux_in_setup)


class TrainingDatapoint(BaseModel):
    aux_io: list[AuxTrainingDatapoint]
    """Aux input and output."""
    proof_output: str
    """Proof to predict."""

    @classmethod
    def from_proof_data(
        cls, setup_data: JGEXSetupData, proof_data: ProofData, aux_tag: str
    ) -> Self:
        return cls(
            aux_io=[AuxTrainingDatapoint.from_setup_data(setup_data, aux_tag)],
            proof_output=_join_proof_steps(proof_data.proof_steps),
        )

    @classmethod
    def from_proof_data_aux_combinations(
        cls, setup_data: JGEXSetupData, proof_data: ProofData, aux_tag: str
    ) -> Self:
        return cls(
            aux_io=AuxTrainingDatapoint.from_setup_data_aux_combinations(
                setup_data, aux_tag
            ),
            proof_output=_join_proof_steps(proof_data.proof_steps),
        )


class AuxTrainingDatapoint(BaseModel):
    input: str
    """Setup and given aux clauses plus the goal."""
    aux_output: str
    """Aux constructions plus theirs predicates to predict."""

    @classmethod
    def from_setup_data(cls, setup_data: JGEXSetupData, aux_tag: str) -> Self:
        goals_str = _join_goals(setup_data.goals)
        return cls(
            input=_join_clauses(setup_data.setup_clauses) + goals_str,
            aux_output=_join_clauses(setup_data.aux_clauses, tag=aux_tag),
        )

    @classmethod
    def from_setup_data_aux_combinations(
        cls, setup_data: JGEXSetupData, aux_tag: str
    ) -> list[Self]:
        goals_str = _join_goals(setup_data.goals)
        aux_clauses = setup_data.aux_clauses

        aux_io: list[Self] = []
        for aux_left_out_index in range(1, len(aux_clauses) + 1):
            aux_included = aux_clauses[:-aux_left_out_index]
            aux_to_predict = aux_clauses[len(aux_clauses) - aux_left_out_index :]
            aux_io.append(
                cls(
                    input=_join_clauses(setup_data.setup_clauses + aux_included)
                    + goals_str,
                    aux_output=_join_clauses(aux_to_predict, tag=aux_tag),
                )
            )
        return aux_io


def _problem_jgex_to_setup_data(
    problem: JGEXFormulation,
    max_attempts: int,
    aux_clauses: list[JGEXClause] | None = None,
    rng: np.random.Generator | None = None,
) -> JGEXSetupData:
    if aux_clauses is None:
        aux_clauses = []
    setup_clauses = [
        clause for clause in problem.setup_clauses if clause not in aux_clauses
    ]
    problem_builder = JGEXProblemBuilder(rng=rng).with_problem(problem)
    jgex_problem_setup = problem_builder.build(
        max_attempts_to_satisfy_goals_numerically=max_attempts
    )
    GeometricSolverBuilder(rng=rng).build(jgex_problem_setup)
    setup_data, _ = jgex_clauses_to_setup_data(
        setup_clauses=setup_clauses,
        aux_clauses=aux_clauses,
        clauses_consequences=problem_builder.clauses_consequences,
        goals=list(problem.goals),
    )
    return setup_data


def _join_goals(goals: list[PredicateConstructionInSetup]) -> str:
    return " ? " + ", ".join(
        _predicate_construction_in_setup_in_proof_to_llm_str(g) for g in goals
    )


def _join_clauses(clauses: list[JGEXClauseInProof], tag: str = "") -> str:
    return "; ".join(_clause_in_proof_to_llm_str(c, tag) for c in clauses)


def _join_proof_steps(proof_steps: list[ProofStep]) -> str:
    return ", ".join(_proof_step_to_llm_str(step) for step in proof_steps)


def _predicate_construction_in_setup_in_proof_to_llm_str(
    predicate_in_prood: PredicateConstructionInSetup,
) -> str:
    return f"[{predicate_in_prood.id}] {_predicate_construction_to_llm_str(predicate_in_prood.construction)}"


def _predicate_in_proof_to_llm_str(
    predicate_in_prood: PredicateInProof,
) -> str:
    return f"[{predicate_in_prood.id}] {_predicate_construction_to_llm_str(predicate_to_construction(predicate_in_prood.predicate))}"


def _predicate_construction_to_llm_str(construction: PredicateConstruction) -> str:
    return (
        construction.predicate_type.value
        + " "
        + " ".join(str(arg) for arg in construction.args)
    )


def _clause_in_proof_to_llm_str(clause: JGEXClauseInProof, tag: str = "") -> str:
    points = " ".join(clause.added_points)
    constructions = ", ".join(
        _jgex_construction_to_llm_str(c) for c in clause.constructions
    )
    if tag:
        tag = tag.strip() + " "
    predicates = ", ".join(
        _predicate_construction_in_setup_in_proof_to_llm_str(pred_construction_in_setup)
        for pred_construction_in_setup in clause.predicates
    )
    return f"{tag}{points} = {constructions} ({predicates})"


def _llm_str_to_clause(llm_str: str) -> JGEXClause:
    points_str, constructions_str = llm_str.split(" = ")
    points = tuple(PredicateArgument(p) for p in points_str.split(" "))
    constructions = tuple(
        _llm_str_to_construction(c_str) for c_str in constructions_str.split(", ")
    )
    return JGEXClause(points=points, constructions=constructions)


def _clauses_in_aux_output(aux_output: str, aux_tag: str) -> list[str]:
    without_aux_tag = aux_output.replace(aux_tag, "")
    without_predicates = re.sub(r"\s*\([^)]*\)", "", without_aux_tag).strip()
    return [s.strip() for s in without_predicates.split(";")]


def _proof_step_to_llm_str(step: ProofStep) -> str:
    premises_str = f"[{','.join(step.applied_on_predicates)}]"
    if step.justification.dependency_type == JustificationType.RULE_APPLICATION:
        reason_str = step.justification.rule.id
    else:
        reason_str = step.justification.dependency_type.value
    return f"{_predicate_in_proof_to_llm_str(step.proven_predicate)} <({reason_str})= {premises_str}"


def _llm_str_to_construction(llm_str: str) -> JGEXConstruction:
    return JGEXConstruction.from_str(llm_str)


def _jgex_construction_to_llm_str(construction: JGEXConstruction) -> str:
    return construction.name + " " + " ".join(str(arg) for arg in construction.args)
