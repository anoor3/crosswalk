from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_rejects_post() -> None:
    assert TestClient(create_app()).post("/jobs/j1/state").status_code == 405
