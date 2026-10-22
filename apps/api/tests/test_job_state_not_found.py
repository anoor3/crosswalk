from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_state_subroute_is_not_found() -> None:
    assert TestClient(create_app()).get("/jobs/j1/state/detail").status_code == 404
