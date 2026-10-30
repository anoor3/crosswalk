from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_get_mapping_route_returns_created_record() -> None:
    client = TestClient(create_app())
    created = client.post(
        "/mappings", json={"tenant_id": "tenant-a", "mapping": {"claim.id": "$.id"}}
    ).json()

    response = client.get(f"/mappings/{created['id']}", params={"tenant_id": "tenant-a"})

    assert response.status_code == 200
    assert response.json()["mapping"] == {"claim.id": "$.id"}
