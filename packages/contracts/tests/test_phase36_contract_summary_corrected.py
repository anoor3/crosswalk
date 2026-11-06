from crosswalk_contracts import ReviewSummaryResponse


def test_summary_corrected() -> None:
    assert (
        ReviewSummaryResponse(
            total=1, open=0, confirmed=0, corrected=1, rejected=0, unresolved=0
        ).corrected
        == 1
    )
