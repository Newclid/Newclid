import traceback
from typing import Any

from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.problem import predicate_to_construction
from newclid.proof_data import proof_data_from_state
from newclid.proof_writing import write_proof, write_proof_sections

from newclid_backend.runner_models import NewclidProofSections, NewclidRunResult
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

    return NewclidProofSections.model_validate(  # noqa: F821
        proof_sections.model_dump()
    )


# This function will not be called directly from our FastAPI backend logic
# This will be directly invoked by a worker
def run_newclid_from_jgex(jgex_problem: str) -> NewclidRunResult:
    try:
        problem_setup = JGEXProblemBuilder().with_problem_from_txt(jgex_problem).build()
        solver = GeometricSolverBuilder().build(problem_setup)

        success = solver.run()

        proof_data = _build_proof_data(solver)
        proof_text = _build_proof_text(proof_data)
        proof_sections = _build_proof_sections(proof_data)
        run_info = _to_run_info_dict(solver.run_infos)

        if success:
            return NewclidRunResult(
                status="succeeded",
                message="Newclid completed successfully.",
                proof_text=proof_text,
                proof_sections=proof_sections,
                run_info=run_info,
            )

        return NewclidRunResult(
            status="failed",
            message="Newclid finished, but did not prove all goals",
            proof_text=proof_text,
            proof_sections=proof_sections,
            run_info=run_info,
        )

    except Exception as error:
        return NewclidRunResult(
            status="failed",
            message=f"Newclid failed: {error}",
            stderr=_truncate_output(traceback.format_exc()),
            proof_text=None,
            proof_sections=None,
            run_info=None,
        )
