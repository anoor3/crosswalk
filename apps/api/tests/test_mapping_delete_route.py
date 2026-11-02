from fastapi.testclient import TestClient

from crosswalk_api import create_app


def test_delete_mapping_route_removes_record() -> None:
    client = TestClient(create_app())
    created = client.post(
        "/mappings", json={"tenant_id": "tenant-a", "mapping": {"a": "b"}}
    ).json()

    response = client.delete(
        f"/mappings/{created['id']}", params={"tenant_id": "tenant-a"}
    )

    assert response.status_code == 204
    assert client.get(f"/mappings/{created['id']}", params={"tenant_id": "tenant-a"}).status_code == 404
