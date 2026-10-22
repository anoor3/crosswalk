from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_enforces_request_limit() -> None:
    response = TestClient(create_app()).get("/jobs/j1/state", headers={"Content-Length": "2000000"})

    assert response.status_code == 413
