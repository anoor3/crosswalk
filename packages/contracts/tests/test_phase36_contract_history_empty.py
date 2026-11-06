from crosswalk_contracts import ReviewHistoryResponse


def test_history_empty() -> None:
    assert ReviewHistoryResponse(review_id="r", actions=()).actions == ()
