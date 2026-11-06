from crosswalk_contracts import ReviewActionResponse, ReviewHistoryResponse


def test_history_action() -> None:
    a = ReviewActionResponse(version=1, action="REJECT", reviewer_id="a", rationale="no")
    assert len(ReviewHistoryResponse(review_id="r", actions=(a,)).actions) == 1
