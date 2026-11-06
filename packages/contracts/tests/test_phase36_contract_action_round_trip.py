from crosswalk_contracts import ReviewActionResponse


def test_action_round_trip() -> None:
    assert (
        ReviewActionResponse(version=1, action="REJECT", reviewer_id="a", rationale="no").action
        == "REJECT"
    )
