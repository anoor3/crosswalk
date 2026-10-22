from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_status_is_uppercase() -> None:
    assert TestClient(create_app()).get("/jobs/j1/state").json()["status"] == "QUEUED"
