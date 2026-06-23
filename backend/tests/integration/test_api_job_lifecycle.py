from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from newclid_backend.runner_models import NewclidRunResult

pytestmark = pytest.mark.redis


def _mock_runner(monkeypatch: pytest.MonkeyPatch, **mock_kwargs: Any) -> Mock:
    runner_mock = Mock(**mock_kwargs)
    monkeypatch.setattr(
        "newclid_backend.newclid_runner.run_newclid_from_jgex",
        runner_mock,
    )
    return runner_mock


def test_successful_job_lifecycle(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    run_burst_worker,
) -> None:
    expected_result = NewclidRunResult(
        status="succeeded",
        message="Newclid completed successfully.",
        proof_text="# Proof",
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
    create_response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": "   a b c = triangle a b c ? perp a b c d   ",
            "custom_theorems": custom_theorems,
        },
    )

    assert create_response.status_code == 200
    create_body = create_response.json()
    assert create_body["status"] == "queued"
    job_id = create_body["job_id"]

    queued_response = client.get(f"/api/jobs/{job_id}")
    assert queued_response.status_code == 200
    assert queued_response.json()["status"] == "queued"

    run_burst_worker()

    runner_mock.assert_called_once_with(
        "a b c = triangle a b c ? perp a b c d",
        custom_theorems=custom_theorems,
    )

    status_response = client.get(f"/api/jobs/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "succeeded"

    result_response = client.get(f"/api/jobs/{job_id}/result")
    assert result_response.status_code == 200
    result_body = result_response.json()
    assert result_body["status"] == "succeeded"
    assert result_body["result"] == expected_result.model_dump()
    assert result_body["error"] is None


def test_failed_result_lifecycle(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    run_burst_worker,
) -> None:
    expected_result = NewclidRunResult(
        status="failed",
        message="Newclid failed: invalid input",
    )
    _mock_runner(monkeypatch, return_value=expected_result)

    create_response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": "a b c = triangle a b c ? perp a b c d",
        },
    )
    job_id = create_response.json()["job_id"]

    run_burst_worker()

    status_response = client.get(f"/api/jobs/{job_id}")
    assert status_response.json()["status"] == "failed"

    result_response = client.get(f"/api/jobs/{job_id}/result")
    result_body = result_response.json()
    assert result_body["status"] == "failed"
    assert result_body["result"] == expected_result.model_dump()
    assert result_body["error"] == "Newclid failed: invalid input"
