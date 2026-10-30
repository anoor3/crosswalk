from fastapi.testclient import TestClient

from crosswalk_api import create_app


def test_update_mapping_route_rejects_stale_version() -> None:
    client = TestClient(create_app())
    created = client.post(
        "/mappings", json={"tenant_id": "tenant-a", "mapping": {"x": "y"}}
    ).json()

    response = client.put(
        f"/mappings/{created['id']}",
        json={"tenant_id": "tenant-a", "expected_version": 2, "mapping": {"x": "z"}},
    )

    assert response.status_code == 409
