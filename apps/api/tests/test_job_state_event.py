from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_records_request_event() -> None:
    client = TestClient(create_app())
    client.get("/jobs/j1/state")

    assert client.get("/events").json()[0]["path"] == "/jobs/j1/state"
