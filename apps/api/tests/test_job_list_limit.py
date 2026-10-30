from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_job_list_rejects_zero_limit() -> None:
    response = TestClient(create_app()).get("/jobs", params={"tenant_id": "t", "limit": 0})
    assert response.status_code == 422
