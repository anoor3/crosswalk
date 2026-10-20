from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_apps_have_independent_default_events() -> None:
    first = TestClient(create_app())
    second = TestClient(create_app())
    first.get("/health")

    assert len(second.get("/events").json()) == 1
