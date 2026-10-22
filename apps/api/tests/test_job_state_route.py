from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_route_returns_queued() -> None:
    response = TestClient(create_app()).get("/jobs/j1/state")

    assert response.json() == {"id": "j1", "status": "QUEUED"}
