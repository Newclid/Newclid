from typing import Any


# This function acts like an adapter between RQ logic and the standalone newclid runner
def run_newclid_job(jgex_problem: str) -> dict[str, Any]:
    from newclid_backend.newclid_runner import run_newclid_from_jgex

    result = run_newclid_from_jgex(jgex_problem)

    return result.model_dump()
