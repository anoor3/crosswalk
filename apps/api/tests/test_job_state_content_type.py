from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_is_json() -> None:
    response = TestClient(create_app()).get("/jobs/j1/state")

    assert response.headers["content-type"].startswith("application/json")
