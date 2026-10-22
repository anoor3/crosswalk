from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_has_security_headers() -> None:
    response = TestClient(create_app()).get("/jobs/j1/state")

    assert response.headers["X-Frame-Options"] == "DENY"
