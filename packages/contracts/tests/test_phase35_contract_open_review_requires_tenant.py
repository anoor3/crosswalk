import pytest
from crosswalk_contracts import (
    OpenReviewRequest,
)
from pydantic import ValidationError


def test_open_review_requires_tenant() -> None:
    with pytest.raises(ValidationError):
        OpenReviewRequest(tenant_id="", review_id="r", candidate={})
