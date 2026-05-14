from typing import Any

from newclid_backend.newclid_runner import run_newclid_from_jgex


def run_newclid_job(jgex_problem: str, timeout_seconds: int) -> dict[str, Any]:
    result = run_newclid_from_jgex(jgex_problem, timeout_seconds)

    return result.model_dump()
