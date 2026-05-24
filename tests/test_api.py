from fastapi.testclient import TestClient

from clawflow.gateway.api import app


def test_api_health_endpoint_works():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

