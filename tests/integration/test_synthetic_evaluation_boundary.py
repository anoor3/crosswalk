from crosswalk_synthetic import generate_api


def test_synthetic_boundary_produces_stable_claim_records() -> None:
    api = generate_api(seed=9, records=2)
    assert api.records[0]["claim_id"] == "clm_9_0"
