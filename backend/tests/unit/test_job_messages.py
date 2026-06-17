from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

import pytest
from newclid_backend.routers import jobs
from newclid_backend.routers.jobs import PublicJobStatus


@pytest.mark.parametrize(
    ("public_status", "expected_message"),
    [
        ("queued", "Job is queued."),
        ("running", "Job is running."),
    ],
)
def test_get_message_for_job_returns_non_terminal_fallback(
    public_status: PublicJobStatus,
    expected_message: str,
) -> None:
    return_value_mock = Mock()
    job = SimpleNamespace(return_value=return_value_mock)

    result = jobs._get_message_for_job(
        job,
        public_status,
    )

    assert result == expected_message
    return_value_mock.assert_not_called()


@pytest.mark.parametrize(
    ("public_status", "job_result", "expected_message"),
    [
        (
            "succeeded",
            {},
            "Newclid completed successfully.",
        ),
        (
            "failed",
            {},
            "Newclid failed.",
        ),
        (
            "succeeded",
            {"status": "succeeded"},
            "Newclid completed successfully.",
        ),
        (
            "failed",
            {"status": "failed"},
            "Newclid failed.",
        ),
    ],
)
def test_get_message_for_job_uses_fallback_when_message_is_missing(
    public_status: PublicJobStatus,
    job_result: dict[str, Any],
    expected_message: str,
) -> None:
    return_value_mock = Mock(return_value=job_result)
    job = SimpleNamespace(return_value=return_value_mock)

    result = jobs._get_message_for_job(
        job,
        public_status,
    )

    assert result == expected_message
    return_value_mock.assert_called_once_with(refresh=True)


@pytest.mark.parametrize(
    ("public_status", "job_result", "expected_message"),
    [
        (
            "succeeded",
            None,
            "Newclid completed successfully.",
        ),
        (
            "failed",
            None,
            "Newclid failed.",
        ),
        (
            "succeeded",
            "unexpected result",
            "Newclid completed successfully.",
        ),
        (
            "failed",
            ["unexpected", "result"],
            "Newclid failed.",
        ),
    ],
)
def test_get_message_for_job_uses_fallback_for_non_dictionary_result(
    public_status: PublicJobStatus,
    job_result: Any,
    expected_message: str,
) -> None:
    return_value_mock = Mock(return_value=job_result)
    job = SimpleNamespace(return_value=return_value_mock)

    result = jobs._get_message_for_job(
        job,
        public_status,
    )

    assert result == expected_message
    return_value_mock.assert_called_once_with(refresh=True)


@pytest.mark.parametrize(
    ("public_status", "invalid_message", "expected_message"),
    [
        (
            "succeeded",
            None,
            "Newclid completed successfully.",
        ),
        (
            "succeeded",
            123,
            "Newclid completed successfully.",
        ),
        (
            "failed",
            False,
            "Newclid failed.",
        ),
        (
            "failed",
            ["Newclid failed"],
            "Newclid failed.",
        ),
    ],
)
def test_get_message_for_job_uses_fallback_for_non_string_message(
    public_status: PublicJobStatus,
    invalid_message: Any,
    expected_message: str,
) -> None:
    return_value_mock = Mock(
        return_value={
            "status": public_status,
            "message": invalid_message,
        }
    )
    job = SimpleNamespace(return_value=return_value_mock)

    result = jobs._get_message_for_job(
        job,
        public_status,
    )

    assert result == expected_message
    return_value_mock.assert_called_once_with(refresh=True)
