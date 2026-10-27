def test_job_state_route_returns_id() -> None:
    from crosswalk_api import create_app
    from fastapi.testclient import TestClient

    assert TestClient(create_app()).get("/jobs/j/state").json()["id"] == "j"
