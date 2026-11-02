from fastapi.testclient import TestClient

from crosswalk_api import create_app


def test_list_mappings_returns_tenant_records() -> None:
    client = TestClient(create_app())
    client.post("/mappings", json={"tenant_id": "tenant-a", "mapping": {"a": "b"}})
    client.post("/mappings", json={"tenant_id": "tenant-b", "mapping": {"c": "d"}})

    response = client.get("/mappings", params={"tenant_id": "tenant-a"})

    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["tenant_id"] == "tenant-a"
