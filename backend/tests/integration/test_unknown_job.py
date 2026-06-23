import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.redis


def test_status_for_unknown_job_returns_404(client: TestClient) -> None:
    response = client.get("/api/jobs/does-not-exist")
    assert response.status_code == 404


def test_result_for_unknown_job_returns_404(client: TestClient) -> None:
    response = client.get("/api/jobs/does-not-exist/result")
    assert response.status_code == 404
