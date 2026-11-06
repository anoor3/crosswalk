from crosswalk_contracts import ReviewActionResponse


def test_action_target() -> None:
    assert (
        ReviewActionResponse(
            version=1,
            action="CORRECT",
            reviewer_id="a",
            canonical_path="claim.id",
            rationale="fixed",
        ).canonical_path
        == "claim.id"
    )
