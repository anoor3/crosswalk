from crosswalk_contracts import ReviewSummaryResponse


def test_summary_unresolved() -> None:
    assert (
        ReviewSummaryResponse(
            total=1, open=0, confirmed=0, corrected=0, rejected=0, unresolved=1
        ).unresolved
        == 1
    )
