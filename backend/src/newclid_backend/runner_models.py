from typing import Any, Literal

from pydantic import BaseModel


class NewclidRunResult(BaseModel):
    status: Literal["succeeded", "failed", "timed_out"]
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    message: str
    proof_text: str | None = None
    run_info: dict[str, Any] | None = None
