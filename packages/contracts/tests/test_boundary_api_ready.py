def test_ready_route_returns_ok() -> None:
    from crosswalk_api import create_app
    from fastapi.testclient import TestClient

    assert TestClient(create_app()).get("/ready").json()["status"] == "ok"
