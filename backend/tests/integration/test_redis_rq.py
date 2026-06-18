from typing import Any
from unittest.mock import Mock

import pytest
from newclid_backend.queue import enqueue_job, fetch_job
from newclid_backend.runner_models import NewclidRunResult
from newclid_backend.tasks import run_newclid_job


def _mock_runner(monkeypatch: pytest.MonkeyPatch, **mock_kwargs: Any) -> Mock:
    runner_mock = Mock(**mock_kwargs)
    monkeypatch.setattr(
        "newclid_backend.newclid_runner.run_newclid_from_jgex",
        runner_mock,
    )
    return runner_mock


def test_enqueued_job_is_fetchable_and_initially_queued() -> None:
    job = enqueue_job(run_newclid_job, "problem text", [], job_id="job-1")

    fetched = fetch_job("job-1")

    assert fetched is not None
    assert fetched.id == job.id
    assert fetched.get_status() == "queued"


def test_burst_worker_runs_task_with_mocked_runner(
    monkeypatch: pytest.MonkeyPatch,
    run_burst_worker,
) -> None:
    expected_result = NewclidRunResult(
        status="succeeded",
        message="Newclid completed successfully.",
    )
    runner_mock = _mock_runner(monkeypatch, return_value=expected_result)

    custom_theorems = [
        {
            "name": "custom_rule",
            "description": "Example rule",
            "premises": ["coll A B C"],
            "conclusions": ["coll C B A"],
        }
    ]
    enqueue_job(
        run_newclid_job,
        "problem text",
        custom_theorems,
        job_id="job-2",
    )

    run_burst_worker()

    runner_mock.assert_called_once_with(
        "problem text",
        custom_theorems=custom_theorems,
    )

    finished = fetch_job("job-2")
    assert finished is not None
    assert finished.get_status() == "finished"
    assert finished.return_value() == expected_result.model_dump()


def test_runner_exception_marks_job_as_failed(
    monkeypatch: pytest.MonkeyPatch,
    run_burst_worker,
) -> None:
    _mock_runner(monkeypatch, side_effect=RuntimeError("solver crashed"))

    enqueue_job(run_newclid_job, "problem text", [], job_id="job-3")

    run_burst_worker()

    failed = fetch_job("job-3")
    assert failed is not None
    assert failed.get_status() == "failed"
