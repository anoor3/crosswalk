from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_increments_request_metric() -> None:
    client = TestClient(create_app())
    client.get("/jobs/j1/state")

    assert client.get("/metrics").json()["requests.total"] == 2
