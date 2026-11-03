from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_confirmed_review_exposes_evaluation_example() -> None:
    client = TestClient(create_app())
    candidate = {
        "external_path": "$.claimNumber",
        "canonical_path": "claim.claim_id",
        "score": 0.8,
        "status": "REVIEW_REQUIRED",
        "evidence": {
            "name": {"score": 1, "weight": 0.45, "reason": "name"},
            "description": {"score": None, "weight": 0.25, "reason": "missing"},
            "type": {"score": 1, "weight": 0.15, "reason": "type"},
            "value_profile": {"score": 0, "weight": 0.15, "reason": "missing"},
        },
    }
    client.post(
        "/reviews", json={"tenant_id": "tenant-a", "review_id": "review-1", "candidate": candidate}
    )
    client.post(
        "/reviews/review-1/decision",
        json={
            "tenant_id": "tenant-a",
            "action": "CONFIRM",
            "reviewer_id": "alice",
            "expected_version": 0,
            "rationale": "The source is the claim identifier.",
            "canonical_path": "claim.claim_id",
        },
    )

    response = client.get("/reviews/review-1/example", params={"tenant_id": "tenant-a"})

    assert response.status_code == 200
    assert response.json()["canonical_path"] == "claim.claim_id"
