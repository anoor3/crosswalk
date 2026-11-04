import pytest
from crosswalk_contracts import (
    OpenReviewRequest,
)
from pydantic import ValidationError


def test_open_review_requires_review_id() -> None:
    with pytest.raises(ValidationError):
        OpenReviewRequest(tenant_id="t", review_id="", candidate={})
