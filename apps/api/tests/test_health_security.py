from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_health_has_security_headers() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.headers["Referrer-Policy"] == "no-referrer"
