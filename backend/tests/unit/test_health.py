from fastapi.testclient import TestClient


def test_health_endpoint_returns_ok(
    client: TestClient,
) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }
