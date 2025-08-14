from typing import Any

import pytest
from ncdgen.generation_configuration import DiagramGenerationConfig


def get_config(**kwargs: Any) -> DiagramGenerationConfig:
    """Returns a valid DiagramGenerationConfig with optional overrides."""
    default_valid_config: dict[str, Any] = {
        "min_pts": 8,
        "max_pts": 10,
        "attempts_per_construction": 1,
        "output_gcs_file": None,
        **kwargs,
    }
    return DiagramGenerationConfig.model_validate(default_valid_config)


def test_valid_config():
    """Tests that a valid config passes validation."""
    get_config()


def test_min_pts_greater_than_max_pts():
    """Tests that validation fails if min_pts > max_pts."""
    with pytest.raises(ValueError, match="min_pts must be less than max_pts"):
        get_config(min_pts=6, max_pts=5)


def test_debug_problem_without_debug_flag():
    """Tests validation fails if debug_problem is set but debug is False."""
    with pytest.raises(
        ValueError, match="Debug mode must be enabled if debug_problem is set"
    ):
        get_config(debug_problem="a problem", debug=False)


class TestPmfSweep:
    def test_pmf_additional_free_points_sweep_invalid_sum(self):
        """Tests validation fails if a pmf in pmf_additional_free_points_sweep sums to != 1."""
        config = get_config(pmf_additional_free_points_sweep=[{0: 3, 1: 3, 2: 2, 3: 2}])
        for pmf in config.pmf_additional_free_points_sweep:
            assert sum(pmf.values()) == 1

    def test_pmf_intersect_vs_other_sweep_invalid_sum(self):
        """Tests validation fails if a pmf in pmf_intersect_vs_other_sweep sums to != 1."""
        config = get_config(pmf_intersect_vs_other_sweep=[{"intersect": 1, "other": 2}])
        for pmf in config.pmf_intersect_vs_other_sweep:
            assert sum(pmf.values()) == 1

    def test_pmf_num_intersecting_to_sample_sweep_invalid_sum(self):
        """Tests validation fails if a pmf in pmf_num_intersecting_to_sample_sweep sums to != 1."""
        config = get_config(pmf_num_intersecting_to_sample_sweep=[{1: 0.5, 2: 0.6}])
        for pmf in config.pmf_num_intersecting_to_sample_sweep:
            assert sum(pmf.values()) == 1
