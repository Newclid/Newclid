"""Helper functions to write proofs in a natural language."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction

from pydantic import BaseModel

from newclid.deductors.deductor_interface import ARDeduction, ARPremise
from newclid.justifications._index import JustificationType
from newclid.justifications.justification import Justification
from newclid.predicates import Predicate
from newclid.proof_data import PredicateInProof, ProofData
from newclid.rule import RuleApplication


class ProofSections(BaseModel):
    points: list[str]
    assumptions: list[str]
    numerical_checks: list[str]
    trivial_predicates: list[str]
    proven_goals: list[str]
    unproven_goals: list[str]
    proof_steps: list[str]
    appendix_ar: list[str]


def write_proof(proof_data: ProofData) -> str:
    """Output the solution to out_file.

    Args:
      proof_state: Proof state.
      problem: Containing the problem definition and theorems.
      out_file: file to write to, empty string to skip writing to file.
    """
    sections = write_proof_sections(proof_data)
    proof_lines: list[str] = ["# Problem setup:"]
    proof_lines.append("\n## Points")
    proof_lines.extend(sections.points)
    proof_lines.append("\n## Assumptions:\n")
    proof_lines.extend(sections.assumptions)
    if sections.numerical_checks:
        proof_lines.append("\n## Numerical checks\n")
        proof_lines.extend(sections.numerical_checks)

    proof_lines.append("\n\n# Goals\n")
    proof_lines.extend(sections.proven_goals)
    if sections.unproven_goals:
        proof_lines.append("\n## Unproven goals")
        proof_lines.extend(sections.unproven_goals)

    proof_lines.append("\n\n# Proof:\n")
    proof_lines.extend(sections.proof_steps)

    proof_lines.append("\n\n# Appendix: AR deductions:")
    proof_lines.extend(sections.appendix_ar)

    proof_lines.append("\nEnd of proof.")

    return "\n".join(proof_lines)


def write_proof_sections(proof_data: ProofData) -> ProofSections:
    point_prefix = "\n- "
    point_lines: list[str] = [
        f"{point_prefix}{point_prefix.join(f'{p}({p.num.x:.4f}, {p.num.y:.4f})' for p in proof_data.points)}"
    ]
    assumption_lines: list[str] = [
        f"[{assumption.id}] : {assumption.predicate}"
        for assumption in proof_data.construction_assumptions
    ]
    numerical_check_lines: list[str] = [
        f"[{numerical_check.id}] : {numerical_check.predicate}"
        for numerical_check in proof_data.numerical_checks
    ]
    trivial_predicates_lines: list[str] = [
        f"[{trivial_predicate.id}] : {trivial_predicate.predicate}"
        for trivial_predicate in proof_data.trivial_predicates
    ]

    proven_goal_lines: list[str] = [
        f"{proven_goal.predicate} : Proved [{proven_goal.id}]"
        for proven_goal in proof_data.proven_goals
    ]
    unproven_goal_lines: list[str] = [
        f"{unproven_goal} : Could not prove"
        for unproven_goal in proof_data.unproven_goals
    ]

    predicate_to_id: dict[Predicate, PredicateInProof] = {}
    for predicate_in_proof in (
        proof_data.construction_assumptions
        + proof_data.numerical_checks
        + proof_data.trivial_predicates
    ):
        predicate_to_id[predicate_in_proof.predicate] = predicate_in_proof

    for proof_step in proof_data.proof_steps:
        predicate_to_id[proof_step.proven_predicate.predicate] = (
            proof_step.proven_predicate
        )

    ar_deductions: list[tuple[int, ARDeduction]] = []
    proof_lines: list[str] = []
    for step_id, proof_step in enumerate(proof_data.proof_steps):
        line = _write_justification_line(
            justification=proof_step.justification,
            predicate_to_id=predicate_to_id,
            ar_deductions=ar_deductions,
            proven_predicate=proof_step.proven_predicate,
            step_id=step_id,
        )
        proof_lines.append(f"{step_id:03d}. | {line}")

    appendix_ar_lines: list[str] = []
    for step_id, ar_deduction in ar_deductions:
        appendix_ar_lines.append("\n\n")
        appendix_ar_lines.extend(_write_ar_deduction_appendix(step_id, ar_deduction))

    return ProofSections(
        points=point_lines,
        assumptions=assumption_lines,
        numerical_checks=numerical_check_lines,
        trivial_predicates=trivial_predicates_lines,
        proven_goals=proven_goal_lines,
        unproven_goals=unproven_goal_lines,
        proof_steps=proof_lines,
        appendix_ar=appendix_ar_lines,
    )


def _write_justification_line(
    justification: Justification,
    predicate_to_id: dict[Predicate, PredicateInProof],
    ar_deductions: list[tuple[int, ARDeduction]],
    proven_predicate: PredicateInProof,
    step_id: int,
) -> str | None:
    match justification.dependency_type:
        case (
            JustificationType.ASSUMPTION
            | JustificationType.NUMERICAL_CHECK
            | JustificationType.REFLEXIVITY
        ):
            return None
        case JustificationType.RULE_APPLICATION:
            return _rule_application_to_line(
                proven_predicate=proven_predicate,
                rule_application=justification,
                predicate_to_id=predicate_to_id,
            )
        case JustificationType.AR_DEDUCTION:
            ar_deductions.append((step_id, justification))
            return _ar_deduction_to_line(
                ar_deduction=justification,
                predicate_to_id=predicate_to_id,
                proven_predicate=proven_predicate,
            )
        case JustificationType.CIRCLE_MERGE:
            return _write_direct_justification_line(
                premises=(justification.circle.justification,),
                reason="Circle merge",
                proven_predicate=proven_predicate,
            )
        case JustificationType.LINE_MERGE:
            return _write_direct_justification_line(
                premises=(justification.direct_justification,),
                reason="Line merge",
                proven_predicate=proven_predicate,
            )
        case JustificationType.DIRECT_CONSEQUENCE:
            return _write_direct_justification_line(
                premises=justification.premises,
                reason="Direct consequence",
                proven_predicate=proven_predicate,
            )
    raise NotImplementedError(
        f"Writing proof for justification {justification} is not implemented"
    )


def _rule_application_to_line(
    proven_predicate: PredicateInProof,
    rule_application: RuleApplication,
    predicate_to_id: dict[Predicate, PredicateInProof],
) -> str:
    premises_in_proof = [
        predicate_to_id[premise] for premise in rule_application.premises
    ]
    premises_txt = ", ".join(
        f"{_predicate_str(premise_in_proof)}" for premise_in_proof in premises_in_proof
    )
    rule_str = rule_application.rule.fullname
    return f"{premises_txt} =({rule_str})> {_predicate_str(proven_predicate)}"


def _ar_deduction_to_line(
    ar_deduction: ARDeduction,
    predicate_to_id: dict[Predicate, PredicateInProof],
    proven_predicate: PredicateInProof,
) -> str:
    if ar_deduction.ar_premises is None:
        raise ValueError(f"AR deduction has no premises: {ar_deduction}")
    premises_in_proof = [
        predicate_to_id[premise.predicate] for premise in ar_deduction.ar_premises
    ]
    premises_txt = ", ".join(
        f"{_predicate_str(premise_in_proof)}" for premise_in_proof in premises_in_proof
    )
    return f"{premises_txt} =({ar_deduction.dependency_type.value})> {_predicate_str(proven_predicate)}"


def _write_direct_justification_line(
    premises: tuple[Predicate, ...],
    reason: str,
    proven_predicate: PredicateInProof,
) -> str:
    premises_txt = ", ".join(str(premise) for premise in premises)
    return f"{premises_txt} =({reason})> {_predicate_str(proven_predicate)}"


def _predicate_str(proven_predicate: PredicateInProof) -> str:
    return f"{str(proven_predicate.predicate)} [{proven_predicate.id}]"


class CarryOver:
    def __init__(self, carry_over: dict[str, Fraction] | None = None):
        if carry_over is None:
            carry_over = defaultdict(lambda: Fraction(0))
        self.carry_over = carry_over

    def update(self, ar_premise: ARPremise) -> CarryOver:
        new_carry_over = self.carry_over.copy()
        for table_column, column_value in ar_premise.coefficient.lhs_terms.items():
            new_carry_over[table_column] += ar_premise.coefficient.coeff * column_value
        return CarryOver(carry_over=new_carry_over)

    def __str__(self) -> str:
        return _pretty_fraction_dict(self.carry_over)


def _pretty_fraction_dict(fraction_dict: dict[str, Fraction]) -> str:
    content = ", ".join(
        f"{_pretty_column_name(column)}: {_fraction_str(value)}"
        for column, value in fraction_dict.items()
        if value != Fraction(0)
    )
    return f"{{{content}}}"


def _fraction_str(fraction: Fraction) -> str:
    return (
        f"{fraction.numerator}/{fraction.denominator}"
        if fraction.denominator != 1
        else str(fraction.numerator)
    )


def _pretty_column_name(column_name: str) -> str:
    return (
        column_name.replace("-", "")
        .replace("|", "")
        .replace("(", "")
        .replace(")", "")
        .replace("∠", "")
        .upper()
    ).replace("^2", "²")


def _write_ar_deduction_appendix(step_id: int, ar_deduction: ARDeduction) -> list[str]:
    if ar_deduction.ar_premises is None:
        raise ValueError(f"AR deduction has no premises: {ar_deduction}")

    ar_lines: list[str] = [
        f"{step_id:03d}. | {ar_deduction.ar_reason.value} to prove {ar_deduction.predicate}:"
    ]

    prefix = "| "
    carry_over = CarryOver()
    for premise in ar_deduction.ar_premises:
        new_carry_over = carry_over.update(premise)
        pretty_lhs = _pretty_fraction_dict(premise.coefficient.lhs_terms)
        ar_lines.append(
            f"{prefix}Premise {premise.predicate} gives a linear equation with coefficients {pretty_lhs}"
        )
        if carry_over.carry_over:
            ar_lines.append(
                f"{prefix}Then {carry_over} + {premise.coefficient.coeff} x {pretty_lhs}"
            )
            ar_lines.append(f"{prefix}   = {new_carry_over}")
        carry_over = new_carry_over

    ar_lines.append(
        f"We are left with a linear equation with coefficients {carry_over} that gives {ar_deduction.predicate}"
    )

    return ar_lines
