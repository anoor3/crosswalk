from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_missing_subroute_is_observable() -> None:
    client = TestClient(create_app())
    response = client.get("/jobs/j1/state/missing")

    assert response.status_code == 404
