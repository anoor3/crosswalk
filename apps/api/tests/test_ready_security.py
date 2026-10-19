from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_ready_has_security_headers() -> None:
    response = TestClient(create_app()).get("/ready")

    assert response.headers["X-Frame-Options"] == "DENY"
