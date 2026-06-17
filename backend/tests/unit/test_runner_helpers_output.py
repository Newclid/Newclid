from unittest.mock import Mock

import pytest
from newclid_backend import runner_helpers


def test_truncate_output_returns_empty_string_for_none() -> None:
    assert runner_helpers._truncate_output(None) == ""


@pytest.mark.parametrize("output", ["", "abcd", "abcde"])
def test_truncate_output_preserves_output_within_limit(
    monkeypatch: pytest.MonkeyPatch, output: str
) -> None:
    monkeypatch.setattr(runner_helpers, "MAX_OUTPUT_CHARS", 5)
    assert runner_helpers._truncate_output(output) == output


def test_truncate_output_keeps_final_characters_when_over_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runner_helpers, "MAX_OUTPUT_CHARS", 5)
    assert runner_helpers._truncate_output("abcdefgh") == "defgh"


def test_to_run_info_dict_returns_none_for_missing_info() -> None:
    assert runner_helpers._to_run_info_dict(None) is None


def test_to_run_info_dict_returns_model_dump() -> None:
    run_info = Mock()
    run_info.model_dump.return_value = {"runtime": 1.5, "success": True, "steps": 4}
    result = runner_helpers._to_run_info_dict(run_info)
    assert result == {"runtime": 1.5, "success": True, "steps": 4}
    run_info.model_dump.assert_called_once_with()
