from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from newclid_backend.routers import jobs


def _request_payload(
    valid_jgex_problem: str,
    description: str,
) -> dict[str, object]:
    return {
        "input_type": "jgex",
        "problem_input": valid_jgex_problem,
        "custom_theorems": [
            {
                "name": "custom_theorem",
                "description": description,
                "premises": ["coll A B C"],
                "conclusions": ["coll C B A"],
            }
        ],
        "timeout_seconds": 120,
    }


def test_create_job_accepts_500_character_theorem_description(
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

    response = client.post(
        "/api/jobs",
        json=_request_payload(
            valid_jgex_problem,
            "d" * 500,
        ),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    enqueue_mock.assert_called_once()


def test_create_job_rejects_501_character_theorem_description(
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

    response = client.post(
        "/api/jobs",
        json=_request_payload(
            valid_jgex_problem,
            "d" * 501,
        ),
    )

    assert response.status_code == 422
    enqueue_mock.assert_not_called()
