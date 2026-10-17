from fastapi.testclient import TestClient

from crosswalk_api import create_app


def test_create_job_rejects_unknown_fields() -> None:
    response = TestClient(create_app()).post(
        "/jobs", json={"tenant_id": "t1", "kind": "discover", "debug": True}
    )

    assert response.status_code == 422
