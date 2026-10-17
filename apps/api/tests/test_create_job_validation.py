from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_create_job_requires_tenant_id() -> None:
    response = TestClient(create_app()).post("/jobs", json={"kind": "discover"})

    assert response.status_code == 422
