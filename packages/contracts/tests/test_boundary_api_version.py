def test_version_route_returns_service() -> None:
    from crosswalk_api import create_app
    from fastapi.testclient import TestClient

    assert TestClient(create_app()).get("/version").json()["version"] == "service"
