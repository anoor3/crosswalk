from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_health_endpoint_uses_shared_contract() -> None:
    response = TestClient(create_app("test")).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "test"}
