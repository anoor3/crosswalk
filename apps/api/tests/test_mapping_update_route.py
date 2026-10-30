from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_update_mapping_route_increments_version() -> None:
    client = TestClient(create_app())
    created = client.post("/mappings", json={"tenant_id": "tenant-a", "mapping": {"x": "y"}}).json()

    response = client.put(
        f"/mappings/{created['id']}",
        json={"tenant_id": "tenant-a", "expected_version": 1, "mapping": {"x": "z"}},
    )

    assert response.status_code == 200
    assert response.json()["version"] == 2
    assert response.json()["mapping"] == {"x": "z"}
