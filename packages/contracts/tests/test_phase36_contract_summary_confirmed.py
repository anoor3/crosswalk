from crosswalk_contracts import ReviewSummaryResponse


def test_summary_confirmed() -> None:
    assert (
        ReviewSummaryResponse(
            total=1, open=0, confirmed=1, corrected=0, rejected=0, unresolved=0
        ).confirmed
        == 1
    )
