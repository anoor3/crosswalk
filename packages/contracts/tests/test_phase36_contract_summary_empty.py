from crosswalk_contracts import ReviewSummaryResponse


def test_summary_empty() -> None:
    assert (
        ReviewSummaryResponse(
            total=0, open=0, confirmed=0, corrected=0, rejected=0, unresolved=0
        ).total
        == 0
    )
