def test_create_job_route_returns_created() -> None:
    from crosswalk_api import create_app
    from fastapi.testclient import TestClient

    response = TestClient(create_app()).post("/jobs", json={"tenant_id": "t", "kind": "sync"})
    assert response.status_code == 201
