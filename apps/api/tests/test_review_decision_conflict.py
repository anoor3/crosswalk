from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_review_decision_route_rejects_stale_version() -> None:
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
    client.post(
        "/reviews/review-1/decision",
        json={
            "tenant_id": "tenant-a",
            "action": "LEAVE_UNRESOLVED",
            "reviewer_id": "alice",
            "expected_version": 0,
            "rationale": "Needs docs.",
        },
    )

    response = client.post(
        "/reviews/review-1/decision",
        json={
            "tenant_id": "tenant-a",
            "action": "REJECT",
            "reviewer_id": "alice",
            "expected_version": 0,
            "rationale": "Stale attempt.",
        },
    )

    assert response.status_code == 409
