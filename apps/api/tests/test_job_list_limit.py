from fastapi.testclient import TestClient

from crosswalk_api import create_app


def test_job_list_rejects_zero_limit() -> None:
    assert TestClient(create_app()).get("/jobs", params={"tenant_id": "t", "limit": 0}).status_code == 422
