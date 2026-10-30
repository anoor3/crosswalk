from fastapi.testclient import TestClient

from crosswalk_api import create_app
from crosswalk_service import ServiceContext


def test_cancel_job_route_updates_context() -> None:
    context = ServiceContext()
    client = TestClient(create_app(context=context))
    created = client.post("/jobs", json={"tenant_id": "tenant-a", "kind": "discover"}).json()

    response = client.post(
        f"/jobs/{created['id']}/cancel", json={"tenant_id": "tenant-a"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
