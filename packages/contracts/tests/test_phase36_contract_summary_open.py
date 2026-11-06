from crosswalk_contracts import ReviewSummaryResponse


def test_summary_open() -> None:
    assert (
        ReviewSummaryResponse(
            total=1, open=1, confirmed=0, corrected=0, rejected=0, unresolved=0
        ).open
        == 1
    )
