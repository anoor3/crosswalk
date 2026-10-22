from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_preserves_trace() -> None:
    response = TestClient(create_app()).get("/jobs/j1/state", headers={"X-Trace-Id": "job-state"})

    assert response.headers["X-Trace-Id"] == "job-state"
