from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_status_rejects_post_method() -> None:
    response = TestClient(create_app()).post("/jobs/job-1")

    assert response.status_code == 405
