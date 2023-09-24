import json

from fastapi.testclient import TestClient

from app import app  # replace with your actual import

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/v1/")
    assert response.status_code == 200
    assert "datetime" in json.loads(response.text)
