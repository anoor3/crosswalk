from fastapi.testclient import TestClient

from crosswalk_api import create_app


def test_create_job_requires_tenant_id() -> None:
    response = TestClient(create_app()).post("/jobs", json={"kind": "discover"})

    assert response.status_code == 422
