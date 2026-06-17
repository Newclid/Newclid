from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from newclid_backend.routers import jobs
from newclid_backend.tasks import run_newclid_job


def test_create_job_strips_surrounding_problem_whitespace(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    valid_jgex_problem: str,
) -> None:
    enqueue_mock = Mock()

    monkeypatch.setattr(
        jobs,
        "enqueue_job",
        enqueue_mock,
    )

    padded_problem = f"\n\t  {valid_jgex_problem}  \t\n"

    response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": padded_problem,
            "custom_theorems": [],
            "timeout_seconds": 45,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "queued"
    assert isinstance(body["job_id"], str)
    assert body["job_id"]

    enqueue_mock.assert_called_once_with(
        run_newclid_job,
        valid_jgex_problem,
        [],
        job_id=body["job_id"],
        timeout_seconds=45,
    )


def test_create_job_preserves_internal_problem_content(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enqueue_mock = Mock()

    monkeypatch.setattr(
        jobs,
        "enqueue_job",
        enqueue_mock,
    )

    normalized_problem = "a b c = triangle a b c\n? cong a b a c"
    padded_problem = f"\n  {normalized_problem}  \n"

    response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": padded_problem,
            "custom_theorems": [],
        },
    )

    assert response.status_code == 200

    body = response.json()

    enqueue_mock.assert_called_once_with(
        run_newclid_job,
        normalized_problem,
        [],
        job_id=body["job_id"],
        timeout_seconds=120,
    )
