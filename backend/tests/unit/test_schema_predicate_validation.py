from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from newclid_backend.routers import jobs


def _request_payload(
    valid_jgex_problem: str,
    *,
    premises: list[str] | None = None,
    conclusions: list[str] | None = None,
) -> dict[str, object]:
    return {
        "input_type": "jgex",
        "problem_input": valid_jgex_problem,
        "custom_theorems": [
            {
                "name": "custom_theorem",
                "description": "Example theorem",
                "premises": (["coll A B C"] if premises is None else premises),
                "conclusions": (["coll C B A"] if conclusions is None else conclusions),
            }
        ],
        "timeout_seconds": 120,
    }


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("premises", []),
        ("conclusions", []),
    ],
)
def test_create_job_rejects_empty_predicate_list(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    valid_jgex_problem: str,
    field_name: str,
    invalid_value: list[str],
) -> None:
    enqueue_mock = Mock()

    monkeypatch.setattr(
        jobs,
        "enqueue_job",
        enqueue_mock,
    )

    overrides: dict[str, Any] = {
        field_name: invalid_value,
    }

    response = client.post(
        "/api/jobs",
        json=_request_payload(
            valid_jgex_problem,
            **overrides,
        ),
    )

    assert response.status_code == 422
    enqueue_mock.assert_not_called()


@pytest.mark.parametrize(
    ("field_name", "invalid_predicate"),
    [
        ("premises", ""),
        ("premises", "   "),
        ("conclusions", ""),
        ("conclusions", "   "),
    ],
)
def test_create_job_rejects_empty_or_whitespace_predicate(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    valid_jgex_problem: str,
    field_name: str,
    invalid_predicate: str,
) -> None:
    enqueue_mock = Mock()

    monkeypatch.setattr(
        jobs,
        "enqueue_job",
        enqueue_mock,
    )

    overrides: dict[str, Any] = {
        field_name: [invalid_predicate],
    }

    response = client.post(
        "/api/jobs",
        json=_request_payload(
            valid_jgex_problem,
            **overrides,
        ),
    )

    assert response.status_code == 422
    enqueue_mock.assert_not_called()


@pytest.mark.parametrize(
    ("field_name", "invalid_predicate"),
    [
        (
            "premises",
            "coll A B\rC",
        ),
        (
            "conclusions",
            "para A B\rC D",
        ),
    ],
)
def test_create_job_rejects_carriage_return_in_predicate(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    valid_jgex_problem: str,
    field_name: str,
    invalid_predicate: str,
) -> None:
    enqueue_mock = Mock()

    monkeypatch.setattr(
        jobs,
        "enqueue_job",
        enqueue_mock,
    )

    overrides: dict[str, Any] = {
        field_name: [invalid_predicate],
    }

    response = client.post(
        "/api/jobs",
        json=_request_payload(
            valid_jgex_problem,
            **overrides,
        ),
    )

    assert response.status_code == 422
    enqueue_mock.assert_not_called()
