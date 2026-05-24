import pytest
from newclid_backend.newclid_runner import run_newclid_from_jgex


@pytest.mark.slow
def test_run_newclid_from_valid_jgex_returns_successful_result(
    valid_jgex_problem: str,
) -> None:
    result = run_newclid_from_jgex(valid_jgex_problem)

    assert result.status == "succeeded"
    assert result.message == "Newclid completed successfully."

    assert result.proof_text is not None
    assert "Proof" in result.proof_text

    assert result.proof_sections is not None
    assert result.proof_sections.proof_steps

    assert result.run_info is not None
    assert result.run_info["success"] is True

    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.slow
def test_run_newclid_from_invalid_jgex_returns_failed_result() -> None:
    result = run_newclid_from_jgex("this is not valid jgex")

    assert result.status == "failed"
    assert result.message.startswith("Newclid failed:")

    assert result.proof_text is None
    assert result.proof_sections is None
    assert result.run_info is None

    assert result.stdout == ""
    assert result.stderr
