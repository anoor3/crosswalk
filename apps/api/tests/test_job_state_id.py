from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_preserves_job_id() -> None:
    assert TestClient(create_app()).get("/jobs/custom/state").json()["id"] == "custom"
