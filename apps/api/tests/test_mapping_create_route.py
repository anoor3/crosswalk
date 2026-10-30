from fastapi.testclient import TestClient

from crosswalk_api import create_app
from crosswalk_service import ServiceContext


def test_create_mapping_route_persists_tenant_record() -> None:
    context = ServiceContext()
    response = TestClient(create_app(context=context)).post(
        "/mappings", json={"tenant_id": "tenant-a", "mapping": {"claim.id": "$.id"}}
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["tenant_id"] == "tenant-a"
    assert payload["version"] == 1
