from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_status_route_returns_shared_contract() -> None:
    response = TestClient(create_app()).get("/jobs/job-1")
    assert response.json() == {"id": "job-1", "status": "queued", "progress": 0}
