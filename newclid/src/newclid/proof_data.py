"""Define the proof data outputed by Newclid then used to write and display the proof."""

from __future__ import annotations

from typing import Iterable, NewType, Self

from pydantic import BaseModel, model_validator

from newclid.justifications._index import JustificationType
from newclid.justifications.justification import Justification, justify_dependency
from newclid.predicates import Predicate, predicate_from_construction
from newclid.problem import PredicateConstruction
from newclid.proof_justifications import goals_justifications
from newclid.proof_state import ProofState
from newclid.symbols.points_registry import Point

ProofId = NewType("ProofId", str)


class PredicateInProof(BaseModel):
    """A predicate in the proof with its unique id."""

    id: ProofId
    predicate: Predicate

    def __str__(self) -> str:
        return f"[{self.id}] {str(self.predicate)}"


class ProofStep(BaseModel):
    """A deduction step of the proof."""

    proven_predicate: PredicateInProof
    justification: Justification
    applied_on_predicates: tuple[ProofId, ...]

    def __str__(self) -> str:
        premises_str = f"[{','.join(self.applied_on_predicates)}]"
        return f"{premises_str} =({self.justification.dependency_type.value})> {self.proven_predicate}"


class ProofData(BaseModel):
    proof_length: int = 0
    """Total length of the proof."""
    proof_rules_length: int = 0
    """Number of rule applications in the proof."""
    points: list[Point]
    """Points in the initial problem setup."""
    proven_goals: list[PredicateInProof]
    """Predicate in proof of goals that were proved."""
    unproven_goals: list[Predicate]
    """Goals to prove from the initial problem that were not proved."""
    construction_assumptions: list[PredicateInProof]
    """Assumptions made initialy by construction."""
    numerical_checks: list[PredicateInProof]
    """Assumptions made by numerical checks."""
    trivial_predicates: list[PredicateInProof]
    """Predicates that are considered trivialy true within the proof."""
    proof_steps: list[ProofStep]
    """Proof steps."""

    @model_validator(mode="after")
    def set_proof_length(self) -> Self:
        self.proof_length = len(self.proof_steps)
        self.proof_rules_length = sum(
            1
            for step in self.proof_steps
            if step.justification.dependency_type == JustificationType.RULE_APPLICATION
        )
        return self


def proof_data_from_state(
    goals_constructions: list[PredicateConstruction],
    proof_state: ProofState,
) -> ProofData:
    goals: list[Predicate] = []
    for goal_construction in goals_constructions:
        goal = predicate_from_construction(
            goal_construction, points_registry=proof_state.symbols.points
        )
        if goal is None:
            raise ValueError(f"Could not construct goal {goal_construction}")
        goals.append(goal)

    justifications_for_proven_goals, goal_is_proven = goals_justifications(
        goals, proof_state
    )
    return proof_justifications_to_proof_data(
        proof_justifications=justifications_for_proven_goals,
        proof_state=proof_state,
        goal_is_proven=goal_is_proven,
    )


def proof_justifications_to_proof_data(
    proof_justifications: Iterable[Justification],
    proof_state: ProofState,
    goal_is_proven: dict[Predicate, bool],
) -> ProofData:
    proof_steps: list[ProofStep] = []
    construction_assumptions: dict[Predicate, ProofId] = {}
    numerical_checks: dict[Predicate, ProofId] = {}
    predicates_proven: dict[Predicate, ProofId] = {}
    trivial_predicates: dict[Predicate, ProofId] = {}
    new_predicates: list[Predicate] = []

    for justification in proof_justifications:
        predicate = justification.predicate
        match justification.dependency_type:
            case (
                JustificationType.RULE_APPLICATION
                | JustificationType.AR_DEDUCTION
                | JustificationType.CIRCLE_MERGE
                | JustificationType.LINE_MERGE
                | JustificationType.DIRECT_CONSEQUENCE
            ):
                pass
            case JustificationType.ASSUMPTION:
                tag = _get_or_create_tag(
                    justification.predicate,
                    construction_assumptions,
                    ProofId(f"C{len(construction_assumptions)}"),
                )
                construction_assumptions[predicate] = tag
                predicates_proven[predicate] = tag
                continue
            case JustificationType.NUMERICAL_CHECK:
                tag = _get_or_create_tag(
                    justification.predicate,
                    numerical_checks,
                    ProofId(f"N{len(numerical_checks)}"),
                )
                numerical_checks[predicate] = tag
                predicates_proven[predicate] = tag
                continue
            case JustificationType.REFLEXIVITY:
                tag = _get_or_create_tag(
                    justification.predicate,
                    trivial_predicates,
                    ProofId(f"T{len(trivial_predicates)}"),
                )
                trivial_predicates[predicate] = tag
                predicates_proven[predicate] = tag
                continue

        tag = _get_or_create_tag(
            justification.predicate,
            predicates_proven | numerical_checks | construction_assumptions,
            ProofId(f"{len(new_predicates)}"),
        )
        depends_on: list[ProofId] = []
        for previous_stmt in justify_dependency(justification, proof_state):
            if previous_stmt not in predicates_proven:
                previous_stmt_dep = proof_state.justify(previous_stmt)
                if (
                    previous_stmt_dep.dependency_type
                    == JustificationType.NUMERICAL_CHECK
                ):
                    tag = _get_or_create_tag(
                        previous_stmt,
                        numerical_checks,
                        ProofId(f"N{len(numerical_checks)}"),
                    )
                    numerical_checks[previous_stmt] = tag
                    predicates_proven[previous_stmt] = tag
                    continue

                else:
                    raise KeyError(
                        "Could not find predicate %s in the list of previously proven predicates: %s",
                        previous_stmt,
                        predicates_proven,
                    )
            depends_on.append(predicates_proven[previous_stmt])

        new_predicates.append(predicate)
        predicates_proven[predicate] = tag
        proof_steps.append(
            ProofStep(
                proven_predicate=PredicateInProof(
                    id=tag, predicate=justification.predicate
                ),
                justification=justification,
                applied_on_predicates=tuple(depends_on),
            )
        )

    proven_goals: list[PredicateInProof] = []
    unproven_goals: list[Predicate] = []
    for goal, is_proven in goal_is_proven.items():
        if is_proven:
            proven_goals.append(
                PredicateInProof(id=predicates_proven[goal], predicate=goal)
            )
        else:
            unproven_goals.append(goal)

    return ProofData(
        points=list(proof_state.problem.points),
        proven_goals=proven_goals,
        unproven_goals=unproven_goals,
        construction_assumptions=[
            PredicateInProof(id=tag, predicate=construction)
            for construction, tag in construction_assumptions.items()
        ],
        numerical_checks=[
            PredicateInProof(id=tag, predicate=construction)
            for construction, tag in numerical_checks.items()
        ],
        trivial_predicates=[
            PredicateInProof(id=tag, predicate=construction)
            for construction, tag in trivial_predicates.items()
        ],
        proof_steps=proof_steps,
    )


def _get_or_create_tag(
    predicate: Predicate,
    existing_predicates: dict[Predicate, ProofId],
    new_tag: ProofId,
) -> ProofId:
    if predicate in existing_predicates:
        return existing_predicates[predicate]
    return new_tag
