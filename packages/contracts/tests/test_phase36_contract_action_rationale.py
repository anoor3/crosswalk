from crosswalk_contracts import ReviewActionResponse


def test_action_rationale() -> None:
    assert (
        ReviewActionResponse(
            version=1, action="REJECT", reviewer_id="a", rationale="explicit"
        ).rationale
        == "explicit"
    )
