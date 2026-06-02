from typing import Any, Literal

from pydantic import BaseModel, Field


class SketchPoint(BaseModel):
    name: str
    x: float
    y: float


class NewclidProofSections(BaseModel):
    points: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    numerical_checks: list[str] = Field(default_factory=list)
    trivial_predicates: list[str] = Field(default_factory=list)
    proven_goals: list[str] = Field(default_factory=list)
    unproven_goals: list[str] = Field(default_factory=list)
    proof_steps: list[str] = Field(default_factory=list)
    appendix_ar: list[str] = Field(default_factory=list)


class NewclidRunResult(BaseModel):
    status: Literal["succeeded", "failed", "timed_out"]
    message: str

    # human-readable full proof
    proof_text: str | None = None

    # Splitted proof in section for easier use from other programs
    proof_sections: NewclidProofSections | None = None

    # Solver statistics
    run_info: dict[str, Any] | None = None

    # Points used by the frontend to draw the final sketch
    sketch_points: list[SketchPoint] = Field(default_factory=list)

    stdout: str = ""
    stderr: str = ""
