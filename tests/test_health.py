
from fastapi.testclient import TestClient

from app.main import app


def test_health_check():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "neural-api",
        "version": "0.1.0",
    }


def test_list_models():
    client = TestClient(app)

    response = client.get("/v1/models")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "simple-network"
