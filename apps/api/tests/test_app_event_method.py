from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_event_records_method_indirectly_by_path() -> None:
    client = TestClient(create_app())
    client.post("/jobs", json={"tenant_id": "t1", "kind": "discover"})

    assert client.get("/events").json()[0]["path"] == "/jobs"
