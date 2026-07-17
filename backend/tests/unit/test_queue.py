from unittest.mock import Mock, sentinel

import pytest
from newclid_backend import queue


def test_enqueue_job_forwards_arguments_and_rq_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enqueue_mock = Mock(return_value=sentinel.job)

    monkeypatch.setattr(
        queue.newclid_queue,
        "enqueue",
        enqueue_mock,
    )

    custom_theorems = [
        {
            "name": "custom_rule",
            "description": "Example custom rule",
            "premises": ["coll A B C"],
            "conclusions": ["coll C B A"],
        }
    ]

    result = queue.enqueue_job(
        sentinel.task,
        "problem text",
        custom_theorems,
        job_id="job-123",
        timeout_seconds=45,
        meta={"source": "unit-test"},
    )

    assert result is sentinel.job

    enqueue_mock.assert_called_once_with(
        sentinel.task,
        "problem text",
        custom_theorems,
        meta={"source": "unit-test"},
        job_id="job-123",
        job_timeout=45,
        result_ttl=queue.RESULT_TTL_SECONDS,
        failure_ttl=queue.FAILURE_TTL_SECONDS,
    )


def test_enqueue_job_uses_configured_default_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enqueue_mock = Mock(return_value=sentinel.job)

    monkeypatch.setattr(
        queue.newclid_queue,
        "enqueue",
        enqueue_mock,
    )

    result = queue.enqueue_job(
        sentinel.task,
        "problem text",
    )

    assert result is sentinel.job

    enqueue_mock.assert_called_once_with(
        sentinel.task,
        "problem text",
        job_id=None,
        job_timeout=queue.DEFAULT_JOB_TIMEOUT_SECONDS,
        result_ttl=queue.RESULT_TTL_SECONDS,
        failure_ttl=queue.FAILURE_TTL_SECONDS,
    )


def test_fetch_job_returns_fetched_job(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fetch_mock = Mock(return_value=sentinel.job)

    monkeypatch.setattr(
        queue.Job,
        "fetch",
        fetch_mock,
    )

    result = queue.fetch_job("job-123")

    assert result is sentinel.job

    fetch_mock.assert_called_once_with(
        "job-123",
        connection=queue.redis_connection,
    )


def test_fetch_job_returns_none_when_job_does_not_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fetch_mock = Mock(
        side_effect=queue.NoSuchJobError,
    )

    monkeypatch.setattr(
        queue.Job,
        "fetch",
        fetch_mock,
    )

    result = queue.fetch_job("missing-job")

    assert result is None

    fetch_mock.assert_called_once_with(
        "missing-job",
        connection=queue.redis_connection,
    )


def test_fetch_job_propagates_unexpected_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fetch_mock = Mock(
        side_effect=RuntimeError("Redis unavailable"),
    )

    monkeypatch.setattr(
        queue.Job,
        "fetch",
        fetch_mock,
    )

    with pytest.raises(
        RuntimeError,
        match="Redis unavailable",
    ):
        queue.fetch_job("job-123")

    fetch_mock.assert_called_once_with(
        "job-123",
        connection=queue.redis_connection,
    )
