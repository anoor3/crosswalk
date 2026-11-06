from crosswalk_contracts import ReviewActionResponse


def test_action_reviewer() -> None:
    assert (
        ReviewActionResponse(
            version=1, action="REJECT", reviewer_id="reviewer", rationale="no"
        ).reviewer_id
        == "reviewer"
    )
