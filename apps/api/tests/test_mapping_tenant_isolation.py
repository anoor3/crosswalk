from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_mapping_read_hides_other_tenant_record() -> None:
    client = TestClient(create_app())
    created = client.post("/mappings", json={"tenant_id": "tenant-a", "mapping": {"x": "y"}}).json()

    response = client.get(f"/mappings/{created['id']}", params={"tenant_id": "tenant-b"})

    assert response.status_code == 404
