from __future__ import annotations

import uuid
from enum import Enum
from pathlib import Path
from typing import Literal, Optional, Self, TypeVar

from numpy.random import Generator as RngGenerator
from pydantic import BaseModel, Field, field_validator, model_validator

T = TypeVar("T")


class IntersectCases(Enum):
    INTERSECT = "intersect"
    OTHER = "other"


class DiagramGenerationConfig(BaseModel):
    min_pts: int
    """ The minimum number of points added to the original diagram. """
    max_pts: int
    """ The maximum number of points added to the original diagram. """

    initial_jgex_problem: Optional[str] = None
    """ If the user provides this, we'll use the JGEX problem as a starting point for the generation. """

    output_gcs_file: str | None = None

    emit_only_double_checked_aux_subproblems: bool = False
    """ If true, we only emit subproblems that require aux constructions. """

    aux_discriminator: Literal["he_point_deps", "newclid_traceback"] = "he_point_deps"
    """ The discriminator to use to split subgoals points into setup and aux points. """

    debug: bool = False
    """ Whether to run in single-process debug mode. """

    debug_problem: Optional[str] = None
    """ If the user provides this, we'll use it as the problem. """

    double_check_probability: float = 1.0
    """ Probability of double-checking the subproblem with and without auxiliary constructions.
    Will only apply to subproblems with at least one auxiliary constructions."""

    skip_aux_setup_pairs_previous_false_positive: bool = True
    """ If true, we will skip subproblems that have an aux setup pair that was a false positive on a previous goal. """

    min_rules_applied: int = 2
    """ The minimum number of rules applied in the subproblem to not be skipped. """

    random_seed: Optional[int] = None
    """ If provided, we will use this seed for the random number generator.
    Otherwise, we will use the current time as a seed.
    """

    attempts_per_diagram_build: int = Field(default=100, ge=1)
    """ How many times we try to find a configuration of points in 2D that satisfy
    the assumptions of the problem.
    """

    max_check_per_predicate: int = Field(default=10, ge=1)
    """ The maximum number of times we will double-check a subproblem with goal of each predicate type within a diagram. """

    construction_counter_reporting_rate: float = Field(default=0.01, ge=0, le=1)
    """ How often we report the construction attempt counters. Should be between 0 and 1. """

    attempts_per_clause: int = Field(default=200, ge=1)
    """ Each time we sample a JGEX clause, we will try to find input arguments that
    work this number of times before giving up on it. The input arguments are sampled
    uniformly at random from the set of all possible input arguments.
    """

    aux_tag: Literal["!aux", ""] = "!aux"
    """ The tag to use for prefixing auxiliary constructions. """

    pmf_additional_free_points_sweep: list[dict[int, float]] = Field(
        default_factory=lambda: [  # type: ignore
            {0: 1},
            {1: 3, 2: 3, 3: 3},
        ],
        validate_default=True,
    )

    pmf_intersect_vs_other_sweep: list[dict[IntersectCases, float]] = Field(
        default_factory=lambda: [
            {IntersectCases.INTERSECT: 0.5, IntersectCases.OTHER: 0.5},
            {IntersectCases.INTERSECT: 0.3, IntersectCases.OTHER: 0.7},
            {IntersectCases.INTERSECT: 0.7, IntersectCases.OTHER: 0.3},
        ],
        validate_default=True,
    )

    pmf_num_intersecting_to_sample_sweep: list[dict[int, float]] = Field(
        default_factory=lambda: [
            {1: 0.7, 2: 0.3},
            {1: 0.5, 2: 0.5},
            {1: 0.3, 2: 0.7},
        ],
        validate_default=True,
    )

    run_uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    timeout: float | None = None
    """ Timeout (in seconds) for the generation process. (Used in tests) """

    n_workers: int | Literal["auto"] = "auto"
    jsonl_dump_file: Path = Path("./datagen.jsonl")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    """ The log level to use for the generation process. """

    @field_validator(
        "pmf_additional_free_points_sweep",
        "pmf_intersect_vs_other_sweep",
        "pmf_num_intersecting_to_sample_sweep",
        mode="after",
    )
    def validate_pmf_sweep(
        cls, pmf_sweep: list[dict[T, float]]
    ) -> list[dict[T, float]]:
        norm_pmf_sweep: list[dict[T, float]] = []
        for pmf in pmf_sweep:
            norm_pmf = _norm_pdf(pmf)
            norm_pmf_sweep.append(norm_pmf)
        return norm_pmf_sweep

    @field_validator("output_gcs_file")
    def validate_output_gcs_file(cls, gcs_file: str | None) -> str | None:
        return gcs_file

    @model_validator(mode="after")
    def validate_min_max_pts(self) -> Self:
        if self.min_pts > self.max_pts:
            raise ValueError("min_pts must be less than max_pts")
        if self.debug_problem is not None and not self.debug:
            raise ValueError("Debug mode must be enabled if debug_problem is set")
        return self


def _norm_pdf(d: dict[T, float]) -> dict[T, float]:
    total = sum(d.values())
    return {k: v / total for k, v in d.items()}


class SweepSelection(BaseModel):
    additional_free_points_sweep_selection: int
    intersect_vs_other_sweep_selection: int
    num_intersecting_to_sample_sweep_selection: int


def sample_sweep_parameters(
    cfg: DiagramGenerationConfig, rng: RngGenerator
) -> SweepSelection:
    """Sample sweep parameters from the configuration and return a new config instance.

    Args:
        cfg: The base configuration to sample from

    Returns:
        A new configuration instance with sampled sweep parameters
    """
    return SweepSelection(
        additional_free_points_sweep_selection=rng.integers(  # pyright: ignore
            len(cfg.pmf_additional_free_points_sweep)
        ),
        intersect_vs_other_sweep_selection=rng.integers(  # pyright: ignore
            len(cfg.pmf_intersect_vs_other_sweep)
        ),
        num_intersecting_to_sample_sweep_selection=rng.integers(  # pyright: ignore
            len(cfg.pmf_num_intersecting_to_sample_sweep)
        ),
    )
