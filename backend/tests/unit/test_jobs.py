from typing import Any

import pytest
from newclid_backend.routers import jobs
from newclid_backend.tasks import run_newclid_job


class FakeJob:
    def __init__(self, rq_status: str, result: dict[str, Any] | None = None) -> None:
        self.rq_status = rq_status
        self.result = result

    def get_status(self, refresh: bool = False) -> str:
        return self.rq_status

    def return_value(self, refresh: bool = False) -> dict[str, Any] | None:
        return self.result


def _successful_runner_result() -> dict[str, Any]:
    return {
        "status": "succeeded",
        "message": "Newclid completed successfully.",
        "proof_text": "# Proof\n\n000. example proof step",
        "proof_sections": {
            "points": ["A(0, 0)", "B(1, 0)"],
            "assumptions": ["[C0] : AB ⟂ CD"],
            "numerical_checks": [],
            "trivial_predicates": [],
            "proven_goals": ["AD ⟂ BC : Proved [0]"],
            "unproven_goals": [],
            "proof_steps": ["000. example proof step"],
            "appendix_ar": [],
        },
        "run_info": {
            "runtime": 0.01,
            "success": True,
            "steps": 1,
        },
        "sketch_points": [
            {"name": "A", "x": 0.0, "y": 0.0},
            {"name": "B", "x": 1.0, "y": 0.0},
        ],
        "stdout": "",
        "stderr": "",
    }


def _failed_runner_result() -> dict[str, Any]:
    return {
        "status": "failed",
        "message": "Newclid failed: invalid input",
        "proof_text": None,
        "proof_sections": None,
        "run_info": None,
        "sketch_points": [],
        "stdout": "",
        "stderr": "Traceback...",
    }


def test_create_job_enqueues_newclid_job(
    client,
    monkeypatch,
    valid_jgex_problem: str,
) -> None:
    captured: dict[str, Any] = {}

    def fake_enqueue_job(
        func,
        *args,
        job_id=None,
        timeout_seconds=120,
        **kwargs,
    ):
        captured["func"] = func
        captured["args"] = args
        captured["job_id"] = job_id
        captured["timeout_seconds"] = timeout_seconds
        captured["kwargs"] = kwargs

    monkeypatch.setattr(jobs, "enqueue_job", fake_enqueue_job)

    response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": valid_jgex_problem,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "queued"
    assert isinstance(body["job_id"], str)

    assert captured["func"] is run_newclid_job
    assert captured["args"] == (valid_jgex_problem, [])
    assert captured["job_id"] == body["job_id"]
    assert captured["timeout_seconds"] == 120
    assert captured["kwargs"] == {}


def test_create_job_uses_requested_timeout(
    client,
    monkeypatch,
    valid_jgex_problem: str,
) -> None:
    captured: dict[str, Any] = {}

    def fake_enqueue_job(
        func,
        *args,
        job_id=None,
        timeout_seconds=120,
        **kwargs,
    ):
        captured["timeout_seconds"] = timeout_seconds

    monkeypatch.setattr(jobs, "enqueue_job", fake_enqueue_job)

    response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": valid_jgex_problem,
            "timeout_seconds": 30,
        },
    )

    assert response.status_code == 200
    assert captured["timeout_seconds"] == 30


def test_create_job_returns_503_when_enqueue_fails(
    client,
    monkeypatch,
    valid_jgex_problem: str,
) -> None:
    def fake_enqueue_job(*args, **kwargs):
        raise RuntimeError("Redis unavailable")

    monkeypatch.setattr(jobs, "enqueue_job", fake_enqueue_job)

    response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": valid_jgex_problem,
        },
    )

    assert response.status_code == 503
    assert "Could not enqueue a new Newclid job" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {
            "input_type": "invalid",
            "problem_input": "some problem",
        },
        {
            "input_type": "jgex",
        },
    ],
)
def test_create_job_rejects_invalid_request_payload(client, payload) -> None:
    response = client.post("/api/jobs", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("rq_status", "expected_status"),
    [
        ("queued", "queued"),
        ("deferred", "queued"),
        ("scheduled", "queued"),
        ("started", "running"),
        ("failed", "failed"),
    ],
)
def test_to_public_status_maps_rq_statuses(
    rq_status: str,
    expected_status: str,
) -> None:
    job = FakeJob(rq_status)

    assert jobs._to_public_status(job) == expected_status


@pytest.mark.parametrize(
    "runner_status",
    ["succeeded", "failed"],
)
def test_to_public_status_uses_runner_status_when_rq_finished(
    runner_status: str,
) -> None:
    job = FakeJob(
        "finished",
        {
            "status": runner_status,
            "message": f"Runner returned {runner_status}.",
        },
    )

    assert jobs._to_public_status(job) == runner_status


def test_to_public_status_returns_failed_for_unknown_finished_result() -> None:
    job = FakeJob("finished", result=None)

    assert jobs._to_public_status(job) == "failed"


def test_check_job_status_returns_message_from_runner_result(
    client,
    monkeypatch,
) -> None:
    fake_result = {
        "status": "succeeded",
        "message": "Custom runner message.",
    }

    monkeypatch.setattr(
        jobs,
        "fetch_job",
        lambda job_id: FakeJob("finished", fake_result),
    )

    response = client.get("/api/jobs/test-job-id")

    assert response.status_code == 200

    body = response.json()

    assert body["job_id"] == "test-job-id"
    assert body["status"] == "succeeded"
    assert body["message"] == "Custom runner message."


def test_check_job_status_returns_default_message_for_running_job(
    client,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        jobs,
        "fetch_job",
        lambda job_id: FakeJob("started"),
    )

    response = client.get("/api/jobs/test-job-id")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "running"
    assert body["message"] == "Job is running."


def test_check_job_status_returns_404_for_missing_job(client, monkeypatch) -> None:
    monkeypatch.setattr(jobs, "fetch_job", lambda job_id: None)

    response = client.get("/api/jobs/missing-job-id")

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("rq_status", "expected_status"),
    [
        ("queued", "queued"),
        ("started", "running"),
    ],
)
def test_check_job_result_returns_no_result_for_incomplete_job(
    client,
    monkeypatch,
    rq_status: str,
    expected_status: str,
) -> None:
    monkeypatch.setattr(
        jobs,
        "fetch_job",
        lambda job_id: FakeJob(rq_status),
    )

    response = client.get("/api/jobs/test-job-id/result")

    assert response.status_code == 200

    body = response.json()

    assert body["job_id"] == "test-job-id"
    assert body["status"] == expected_status
    assert body["result"] is None
    assert body["error"] is None


def test_check_job_result_returns_proof_output_for_finished_job(
    client,
    monkeypatch,
) -> None:
    fake_result = _successful_runner_result()

    monkeypatch.setattr(
        jobs,
        "fetch_job",
        lambda job_id: FakeJob("finished", fake_result),
    )

    response = client.get("/api/jobs/test-job-id/result")

    assert response.status_code == 200

    body = response.json()

    assert body["job_id"] == "test-job-id"
    assert body["status"] == "succeeded"
    assert body["error"] is None
    assert body["result"] == fake_result
    assert body["result"]["proof_text"] == "# Proof\n\n000. example proof step"
    assert body["result"]["proof_sections"]["proof_steps"] == [
        "000. example proof step"
    ]
    assert body["result"]["run_info"]["success"] is True


@pytest.mark.parametrize(
    "runner_status",
    ["failed"],
)
def test_check_job_result_returns_error_for_unsuccessful_runner_result(
    client,
    monkeypatch,
    runner_status: str,
) -> None:
    fake_result = _failed_runner_result()
    fake_result["status"] = runner_status

    monkeypatch.setattr(
        jobs,
        "fetch_job",
        lambda job_id: FakeJob("finished", fake_result),
    )

    response = client.get("/api/jobs/test-job-id/result")

    assert response.status_code == 200

    body = response.json()

    assert body["job_id"] == "test-job-id"
    assert body["status"] == runner_status
    assert body["result"] == fake_result
    assert body["error"] == "Newclid failed: invalid input"


def test_check_job_result_returns_failed_for_unknown_finished_result(
    client,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        jobs,
        "fetch_job",
        lambda job_id: FakeJob("finished", result=None),
    )

    response = client.get("/api/jobs/test-job-id/result")

    assert response.status_code == 200

    body = response.json()

    assert body["job_id"] == "test-job-id"
    assert body["status"] == "failed"
    assert body["result"] is None
    assert body["error"] == "Newclid job failed for unknown reason"


def test_check_job_result_returns_404_for_missing_job(client, monkeypatch) -> None:
    monkeypatch.setattr(jobs, "fetch_job", lambda job_id: None)

    response = client.get("/api/jobs/missing-job-id/result")

    assert response.status_code == 404


def test_create_job_enqueues_custom_theorems(
    client,
    monkeypatch,
    valid_jgex_problem: str,
) -> None:
    captured: dict[str, Any] = {}

    def fake_enqueue_job(
        func,
        *args,
        job_id=None,
        timeout_seconds=120,
        **kwargs,
    ):
        captured["func"] = func
        captured["args"] = args
        captured["job_id"] = job_id
        captured["timeout_seconds"] = timeout_seconds
        captured["kwargs"] = kwargs

    monkeypatch.setattr(jobs, "enqueue_job", fake_enqueue_job)

    custom_theorems = [
        {
            "name": "custom_parallel_theorem",
            "description": "Perpendiculars to the same line are parallel",
            "premises": [
                "perp A B C D",
                "perp E F C D",
            ],
            "conclusions": [
                "para A B E F",
            ],
        }
    ]

    response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": valid_jgex_problem,
            "custom_theorems": custom_theorems,
        },
    )

    assert response.status_code == 200

    assert captured["func"] is run_newclid_job
    assert captured["args"] == (valid_jgex_problem, custom_theorems)
    assert captured["timeout_seconds"] == 120
    assert captured["kwargs"] == {}
