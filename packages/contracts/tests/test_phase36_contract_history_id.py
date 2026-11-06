from crosswalk_contracts import ReviewHistoryResponse


def test_history_id() -> None:
    assert ReviewHistoryResponse(review_id="review-7", actions=()).review_id == "review-7"
