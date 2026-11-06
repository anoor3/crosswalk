from crosswalk_contracts import ReviewSummaryResponse


def test_summary_rejected() -> None:
    assert (
        ReviewSummaryResponse(
            total=1, open=0, confirmed=0, corrected=0, rejected=1, unresolved=0
        ).rejected
        == 1
    )
