import pytest
from crosswalk_contracts import (
    OpenReviewRequest,
)
from pydantic import ValidationError


def test_open_review_rejects_extra() -> None:
    with pytest.raises(ValidationError):
        OpenReviewRequest(tenant_id="t", review_id="r", candidate={}, extra="x")
