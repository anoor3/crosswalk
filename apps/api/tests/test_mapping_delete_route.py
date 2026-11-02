from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_delete_mapping_route_removes_record() -> None:
    client = TestClient(create_app())
    created = client.post("/mappings", json={"tenant_id": "tenant-a", "mapping": {"a": "b"}}).json()

    response = client.delete(f"/mappings/{created['id']}", params={"tenant_id": "tenant-a"})

    assert response.status_code == 204
    follow_up = client.get(f"/mappings/{created['id']}", params={"tenant_id": "tenant-a"})
    assert follow_up.status_code == 404
