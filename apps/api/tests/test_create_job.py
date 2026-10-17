from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_create_job_accepts_shared_request_contract() -> None:
    response = TestClient(create_app()).post("/jobs", json={"tenant_id": "t1", "kind": "discover"})
    assert response.status_code == 201
    assert response.json()["status"] == "queued"
