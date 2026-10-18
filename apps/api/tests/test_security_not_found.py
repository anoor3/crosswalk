from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_security_headers_apply_to_not_found() -> None:
    response = TestClient(create_app()).get("/missing")

    assert response.headers["X-Frame-Options"] == "DENY"
