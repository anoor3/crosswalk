from crosswalk_contracts import ReviewActionResponse


def test_action_version() -> None:
    assert (
        ReviewActionResponse(version=3, action="REJECT", reviewer_id="a", rationale="no").version
        == 3
    )
