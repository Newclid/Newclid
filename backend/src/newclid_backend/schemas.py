from typing import Any, Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator


class CustomTheoremRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z_][A-Za-z0-9_-]*$",
        description="Unique custom theorem name/id. Must not contain spaces.",
    )
    description: str = Field(
        default="",
        max_length=500,
        description="Human-readable description of the custom theorem.",
    )
    premises: list[str] = Field(
        min_length=1,
        description="Predicate assumptions required by the theorem.",
    )
    conclusions: list[str] = Field(
        min_length=1,
        description="Predicate conclusions produced by the theorem.",
    )

    @field_validator("premises", "conclusions")
    @classmethod
    def validate_predicate_lines(cls, predicates: list[str]) -> list[str]:
        cleaned = [predicate.strip() for predicate in predicates]

        if any(not predicate for predicate in cleaned):
            raise ValueError("Predicates cannot be empty")

        for predicate in cleaned:
            if "\n" in predicate or "\r" in predicate:
                raise ValueError("Predicates must be single-line strings")

            if "=>" in predicate:
                raise ValueError(
                    "Predicates must be individual predicate strings, not full theorem expressions"
                )

        return cleaned


class CreateJobRequest(BaseModel):
    input_type: Literal["jgex"] = Field(
        default="jgex", description="Input format of the submitted problem"
    )
    problem_input: str = Field(description="Problem definition and goal in JGEX format")
    custom_theorems: list[CustomTheoremRequest] = Field(
        default_factory=list, description="Optional custom theorems"
    )
    timeout_seconds: int = Field(
        default=120,
        description="Timeout time after which the newclid process will be stopped",
    )

    @model_validator(mode="after")
    def validate_custom_theorem_names(self) -> Self:
        theorem_names = [theorem.name for theorem in self.custom_theorems]

        if len(theorem_names) != len(set(theorem_names)):
            raise ValueError("Custom theorem names must be unique")

        return self


class CreateJobResponse(BaseModel):
    job_id: str
    status: Literal["queued"]


class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal[
        "queued", "running", "succeeded", "failed", "timed_out", "cancelled"
    ]
    message: str | None = None


class JobResultResponse(BaseModel):
    job_id: str
    status: Literal[
        "queued", "running", "succeeded", "failed", "timed_out", "cancelled"
    ]
    result: dict[str, Any] | None = None
    error: str | None = None
