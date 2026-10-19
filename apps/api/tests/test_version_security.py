from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_version_has_security_headers() -> None:
    response = TestClient(create_app()).get("/version")

    assert response.headers["X-Frame-Options"] == "DENY"
