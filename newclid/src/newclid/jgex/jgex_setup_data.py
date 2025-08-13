from __future__ import annotations

from typing import TYPE_CHECKING, NewType

from pydantic import BaseModel

from newclid.jgex.clause import JGEXClause, JGEXConstruction
from newclid.problem import PredicateConstruction

if TYPE_CHECKING:
    from newclid.jgex.to_newclid import JGEXClauseConsequences

JGEXSetupId = NewType("JGEXSetupId", str)


class PredicateConstructionInSetup(BaseModel):
    id: JGEXSetupId
    construction: PredicateConstruction

    def __str__(self) -> str:
        return f"[{self.id}] {str(self.construction)}"


class JGEXClauseInProof(BaseModel):
    """Constructions of a clause and their resulting predicates."""

    added_points: tuple[str, ...]
    constructions: tuple[JGEXConstruction, ...]
    predicates: tuple[PredicateConstructionInSetup, ...]

    def __str__(self) -> str:
        points = " ".join(self.added_points)
        constructions = ", ".join(str(c) for c in self.constructions)
        predicates = ", ".join(str(s_in_proof) for s_in_proof in self.predicates)
        return f"{points} = {constructions} ({predicates})"


class JGEXSetupData(BaseModel):
    setup_clauses: list[JGEXClauseInProof]
    """The necessary problem constuctions and their consequence predicates."""
    aux_clauses: list[JGEXClauseInProof]
    """The auxiliary constructions and their consequence predicates."""
    goals: list[PredicateConstructionInSetup]
    """Goal predicates."""


def jgex_clauses_to_setup_data(
    setup_clauses: list[JGEXClause],
    aux_clauses: list[JGEXClause],
    goals: list[PredicateConstruction],
    clauses_consequences: dict[JGEXClause, JGEXClauseConsequences],
) -> tuple[JGEXSetupData, dict[JGEXSetupId, PredicateConstruction]]:
    predicates_ids: dict[JGEXSetupId, PredicateConstruction] = {}
    construction_predicates: dict[JGEXSetupId, PredicateConstruction] = {}
    setup_clauses_in_proof = _assign_clauses_predicates(
        clauses=setup_clauses,
        clauses_consequences=clauses_consequences,
        predicates_ids=predicates_ids,
        construction_predicates=construction_predicates,
    )
    aux_clauses_in_proof = _assign_clauses_predicates(
        clauses=aux_clauses,
        clauses_consequences=clauses_consequences,
        predicates_ids=predicates_ids,
        construction_predicates=construction_predicates,
    )
    goals_in_proof = _assign_goals_predicates(goals, predicates_ids)
    setup_data = JGEXSetupData(
        setup_clauses=setup_clauses_in_proof,
        aux_clauses=aux_clauses_in_proof,
        goals=goals_in_proof,
    )
    return setup_data, predicates_ids


def _assign_goals_predicates(
    goals: list[PredicateConstruction],
    predicates_ids: dict[JGEXSetupId, PredicateConstruction],
) -> list[PredicateConstructionInSetup]:
    goals_in_proof: list[PredicateConstructionInSetup] = []
    for index, goal in enumerate(goals):
        goal_tag = JGEXSetupId(f"G{index}")
        if goal_tag in predicates_ids:
            raise ValueError(f"Goal {goal} already has a predicate id")
        predicates_ids[goal_tag] = goal
        goals_in_proof.append(
            PredicateConstructionInSetup(id=goal_tag, construction=goal)
        )
    return goals_in_proof


def _assign_clauses_predicates(
    clauses: list[JGEXClause],
    clauses_consequences: dict[JGEXClause, JGEXClauseConsequences],
    predicates_ids: dict[JGEXSetupId, PredicateConstruction],
    construction_predicates: dict[JGEXSetupId, PredicateConstruction],
) -> list[JGEXClauseInProof]:
    return [
        _assign_clause_predicates(
            clause, clauses_consequences, predicates_ids, construction_predicates
        )
        for clause in clauses
    ]


def _assign_clause_predicates(
    clause: JGEXClause,
    clauses_consequences: dict[JGEXClause, JGEXClauseConsequences],
    predicates_ids: dict[JGEXSetupId, PredicateConstruction],
    construction_predicates: dict[JGEXSetupId, PredicateConstruction],
) -> JGEXClauseInProof:
    clause_predicates_in_proof: list[PredicateConstructionInSetup] = []
    constructions = clauses_consequences[clause].construction_consequences
    for construction_consequence in constructions:
        for predicate_construction in construction_consequence.added_predicates:
            n_predicates = len(construction_predicates)
            tag = JGEXSetupId(f"C{n_predicates}")
            if tag in predicates_ids:
                raise ValueError(
                    f"Tag {tag} already has predicate {predicates_ids[tag]} attributed to it"
                )
            predicates_ids[tag] = predicate_construction
            construction_predicates[tag] = predicate_construction
            clause_predicates_in_proof.append(
                PredicateConstructionInSetup(
                    id=tag, construction=predicate_construction
                )
            )
    return JGEXClauseInProof(
        constructions=clause.constructions,
        predicates=tuple(clause_predicates_in_proof),
        added_points=clause.points,
    )
