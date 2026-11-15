import pytest
from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_example_discovery_can_be_reviewed() -> None:
    with TestClient(create_app()) as client:
        example = client.get("/workbench/example").json()
        result = client.post("/workbench/analyze", json=example)
        assert result.status_code == 200
        data = result.json()
        assert len(data["candidates"]) == len(data["endpoint"]["response_fields"]) > 0
        candidate = data["candidates"][0]
        opened = client.post(
            "/reviews",
            json={
                "tenant_id": "workbench-test",
                "review_id": "field-1",
                "candidate": candidate,
            },
        )
        assert opened.status_code == 201
        decision = client.post(
            "/reviews/field-1/decision",
            json={
                "tenant_id": "workbench-test",
                "expected_version": 0,
                "action": "REJECT",
                "reviewer_id": "Tester",
                "rationale": "Verify a different target",
            },
        )
        assert decision.status_code == 200
        assert decision.json()["state"] == "REJECTED"


def test_unknown_endpoint_and_invalid_document_fail_cleanly() -> None:
    with TestClient(create_app()) as client:
        example = client.get("/workbench/example").json()
        example["path"] = "/missing"
        assert client.post("/workbench/analyze", json=example).status_code == 422
        assert client.post("/workbench/analyze", json={"spec": {}}).status_code == 422


def test_workbench_assets_are_served() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/").url.path == "/workspace/"
        for file in ("index.html", "app.js", "style.css"):
            assert client.get("/workspace/" + file).status_code == 200


def test_remote_openapi_returns_a_clear_fetch_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from crosswalk_api import workbench
    from crosswalk_api.remote_import import RemoteImportError

    def reject(_url: str) -> None:
        raise RemoteImportError("redirects are blocked")

    monkeypatch.setattr(workbench, "fetch_openapi", reject)
    with TestClient(create_app()) as client:
        response = client.post(
            "/workbench/remote-openapi", json={"url": "https://example.com/openapi.json"}
        )
    assert response.status_code == 422
    assert response.json()["detail"] == "redirects are blocked"
