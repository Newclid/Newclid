import traceback

from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder

from newclid_backend.runner_models import NewclidRunResult
from newclid_backend.settings import MAX_OUTPUT_CHARS


def _truncate_output(output: str | None) -> str:
    if output is None:
        return ""

    if len(output) <= MAX_OUTPUT_CHARS:
        return output

    return output[-MAX_OUTPUT_CHARS:]


# This function will not be called directly from our FastAPI backend logic
# This will be directly invoked by a worker
def run_newclid_from_jgex(jgex_problem: str) -> NewclidRunResult:
    try:
        problem_setup = JGEXProblemBuilder().with_problem_from_txt(jgex_problem).build()

        solver = GeometricSolverBuilder().build(problem_setup)

        success = solver.run()
        proof_text = solver.proof()

        if success:
            return NewclidRunResult(
                status="succeeded",
                message="Newclid completed successfully.",
                proof_text=_truncate_output(proof_text),
            )

        return NewclidRunResult(
            status="failed",
            message="Newclid finished, but did not prove all goals",
            proof_text=_truncate_output(proof_text),
        )

    except Exception as error:
        return NewclidRunResult(
            status="failed",
            message=f"Newclid failed: {error}",
            stderr=_truncate_output(traceback.format_exc()),
            proof_text=None,
            run_info=None,
        )
