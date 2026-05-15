import subprocess

from newclid_backend.runner_models import NewclidRunResult
from newclid_backend.settings import MAX_OUTPUT_CHARS, NEWCLID_COMMAND


def _truncate_output(output: str | None) -> str:
    if output is None:
        return ""

    if len(output) <= MAX_OUTPUT_CHARS:
        return output

    return output[-MAX_OUTPUT_CHARS:]


# This function will not be called directly from our FastAPI backend logic
# This will be directly invoked by a worker
def run_newclid_from_jgex(jgex_problem: str, timeout_seconds: int) -> NewclidRunResult:
    command = [NEWCLID_COMMAND, "jgex", "--problem", jgex_problem]

    try:
        completed_process = subprocess.run(
            command,
            capture_output=True,
            text=True,  # return stdout/stderr as strings
            timeout=timeout_seconds,
            check=False,  # do not throw an exception just because Newclid exits with error code
        )
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout if isinstance(error.stdout, str) else ""
        stderr = error.stderr if isinstance(error.stderr, str) else ""

        return NewclidRunResult(
            status="timed_out",
            return_code=None,
            stdout=_truncate_output(stdout),
            stderr=_truncate_output(stderr),
            message=f"Newclid exceeded the timeout of {timeout_seconds} seconds.",
        )

    stdout = _truncate_output(completed_process.stdout)
    stderr = _truncate_output(completed_process.stderr)

    if completed_process.returncode == 0:
        return NewclidRunResult(
            status="succeeded",
            return_code=0,
            stdout=_truncate_output(stdout),
            stderr=_truncate_output(stderr),
            message="Newclid completed successfully",
        )

    return NewclidRunResult(
        status="failed",
        return_code=completed_process.returncode,
        stdout=_truncate_output(stdout),
        stderr=_truncate_output(stderr),
        message="Newclid failed",
    )
