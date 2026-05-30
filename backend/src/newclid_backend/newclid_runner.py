import traceback
from typing import Any

from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.problem import predicate_to_construction
from newclid.proof_data import proof_data_from_state
from newclid.proof_writing import write_proof, write_proof_sections
from newclid.rule import Rule

from newclid_backend.runner_models import (
    NewclidProofSections,
    NewclidRunResult,
    SketchPoint,
)
from newclid_backend.settings import MAX_OUTPUT_CHARS


def _truncate_output(output: str | None) -> str:
    if output is None:
        return ""

    if len(output) <= MAX_OUTPUT_CHARS:
        return output

    return output[-MAX_OUTPUT_CHARS:]


def _to_run_info_dict(run_info: Any) -> dict[str, Any] | None:
    if run_info is None:
        return None

    return run_info.model_dump()


def _build_proof_data(solver: Any) -> Any:
    goals_constructions = [
        predicate_to_construction(goal) for goal in solver.proof_state.goals
    ]

    return proof_data_from_state(
        goals_constructions=goals_constructions, proof_state=solver.proof_state
    )


def _build_proof_text(proof_data: Any) -> str:
    return _truncate_output(write_proof(proof_data))


def _build_proof_sections(proof_data: Any) -> NewclidProofSections:
    proof_sections = write_proof_sections(proof_data)

    return NewclidProofSections.model_validate(proof_sections.model_dump())


def _build_custom_rules(custom_rules: list[dict[str, Any]]) -> list[Rule]:
    return [
        Rule(
            id=rule["name"],
            description=rule.get("description") or rule["name"],
            premises_txt=list(rule["premises"]),
            conclusions_txt=list(rule["conclusions"]),
        )
        for rule in custom_rules
    ]


# This function will not be called directly from our FastAPI backend logic
# This will be directly invoked by a worker
def _build_sketch_points(proof_data: Any) -> list[SketchPoint]:
    return [
        SketchPoint(name=p.name, x=float(p.num.x), y=float(p.num.y))
        for p in proof_data.points
    ]


def run_newclid_from_jgex(
    jgex_problem: str, custom_rules: list[dict[str, Any]] | None = None
) -> NewclidRunResult:
    try:
        problem_setup = JGEXProblemBuilder().with_problem_from_txt(jgex_problem).build()
        solver_builder = GeometricSolverBuilder()

        if custom_rules:
            solver_builder.with_additional_rules(_build_custom_rules(custom_rules))

        solver = solver_builder.build(problem_setup)

        success = solver.run()
        run_info = _to_run_info_dict(solver.run_infos)

        if not success:
            return NewclidRunResult(
                status="failed",
                message="Newclid finished, but did not prove all goals.",
                proof_text=None,
                proof_sections=None,
                run_info=run_info,
                sketch_points=[],
            )

        proof_data = _build_proof_data(solver)
        proof_text = _build_proof_text(proof_data)
        proof_sections = _build_proof_sections(proof_data)
        sketch_points = _build_sketch_points(proof_data)

        return NewclidRunResult(
            status="succeeded",
            message="Newclid completed successfully.",
            proof_text=proof_text,
            proof_sections=proof_sections,
            run_info=run_info,
            sketch_points=sketch_points,
        )

    except Exception as error:
        return NewclidRunResult(
            status="failed",
            message=f"Newclid failed: {error}",
            stderr=_truncate_output(traceback.format_exc()),
            proof_text=None,
            proof_sections=None,
            run_info=None,
            sketch_points=[],
        )
