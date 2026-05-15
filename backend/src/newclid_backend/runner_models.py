from typing import Literal

from pydantic import BaseModel


class NewclidRunResult(BaseModel):
    status: Literal["succeeded", "failed", "timed_out"]
    return_code: int | None
    stdout: str
    stderr: str
    message: str
