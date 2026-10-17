from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_create_job_rejects_blank_tenant() -> None:
    response = TestClient(create_app()).post("/jobs", json={"tenant_id": "", "kind": "discover"})

    assert response.status_code == 422
