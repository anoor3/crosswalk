import pytest
from crosswalk_contracts import (
    ReviewDecisionRequest,
)
from pydantic import ValidationError


def test_decision_rejects_negative_version() -> None:
    with pytest.raises(ValidationError):
        ReviewDecisionRequest(
            tenant_id="t", action="REJECT", reviewer_id="a", expected_version=-1, rationale="x"
        )
