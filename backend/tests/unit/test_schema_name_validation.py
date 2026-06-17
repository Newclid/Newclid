from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from newclid_backend.routers import jobs


def _request_payload(
    valid_jgex_problem: str,
    theorem_name: str,
) -> dict[str, object]:
    return {
        "input_type": "jgex",
        "problem_input": valid_jgex_problem,
        "custom_theorems": [
            {
                "name": theorem_name,
                "description": "Example theorem",
                "premises": ["coll A B C"],
                "conclusions": ["coll C B A"],
            }
        ],
        "timeout_seconds": 120,
    }


@pytest.mark.parametrize(
    "invalid_name",
    [
        "1custom_theorem",
        "custom theorem",
        "custom.theorem",
        "custom@theorem",
    ],
)
def test_create_job_rejects_invalid_custom_theorem_name(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    valid_jgex_problem: str,
    invalid_name: str,
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
            invalid_name,
        ),
    )

    assert response.status_code == 422
    enqueue_mock.assert_not_called()


def test_create_job_accepts_100_character_custom_theorem_name(
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

    theorem_name = "a" * 100

    response = client.post(
        "/api/jobs",
        json=_request_payload(
            valid_jgex_problem,
            theorem_name,
        ),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    enqueue_mock.assert_called_once()


def test_create_job_rejects_101_character_custom_theorem_name(
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

    theorem_name = "a" * 101

    response = client.post(
        "/api/jobs",
        json=_request_payload(
            valid_jgex_problem,
            theorem_name,
        ),
    )

    assert response.status_code == 422
    enqueue_mock.assert_not_called()
