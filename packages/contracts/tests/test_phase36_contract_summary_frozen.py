import pytest
from crosswalk_contracts import ReviewSummaryResponse


def test_summary_frozen() -> None:
    value = ReviewSummaryResponse(
        total=0, open=0, confirmed=0, corrected=0, rejected=0, unresolved=0
    )
    with pytest.raises(Exception):  # noqa: B017
        value.total = 1  # type: ignore[misc]
