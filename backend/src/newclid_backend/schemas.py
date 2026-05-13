from typing import Literal

from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    input_type: Literal["jgex"] = Field(
        default="jgex", description="Input format of the submitted problem"
    )
    problem_input: str = Field(description="Problem definition in JGEX format")
    goals: str = Field(description="Goal that Newclid should try to prove.")
    timeout_seconds: int = Field(
        default=120,
        description="Timeout time after which the newclid process will be stopped",
    )


class CreateJobResponse(BaseModel):
    job_id: str
    status: Literal["queued"]


class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal[
        "queued", "running", "succeeded", "failed", "timed_out", "cancelled"
    ]
    message: str | None = None
