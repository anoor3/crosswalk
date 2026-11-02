from fastapi.testclient import TestClient

from crosswalk_api import create_app


def test_review_decision_route_records_leave_unresolved() -> None:
    client = TestClient(create_app())
    client.post(
        "/reviews",
        json={
            "tenant_id": "tenant-a",
            "review_id": "review-1",
            "candidate": {
                "external_path": "$.id",
                "canonical_path": None,
                "score": 0,
                "status": "UNRESOLVED",
                "evidence": None,
            },
        },
    )

    response = client.post(
        "/reviews/review-1/decision",
        json={
            "tenant_id": "tenant-a",
            "action": "LEAVE_UNRESOLVED",
            "reviewer_id": "alice",
            "expected_version": 0,
            "rationale": "Needs source documentation.",
        },
    )

    assert response.status_code == 200
    assert response.json()["state"] == "UNRESOLVED"
    assert response.json()["version"] == 1
