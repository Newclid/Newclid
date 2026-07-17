from typing import Any


# This function acts like an adapter between RQ logic and the standalone newclid runner
def run_newclid_job(
    jgex_problem: str, custom_theorems: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    from newclid_backend.newclid_runner import run_newclid_from_jgex

    result = run_newclid_from_jgex(jgex_problem, custom_theorems=custom_theorems)

    return result.model_dump()
