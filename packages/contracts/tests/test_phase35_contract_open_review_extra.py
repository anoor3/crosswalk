import pytest
from pydantic import ValidationError
from crosswalk_contracts import EvaluationExampleResponse, OpenReviewRequest, ReviewDecisionRequest, ReviewResponse

def test_open_review_rejects_extra() -> None:
    with pytest.raises(ValidationError): OpenReviewRequest(tenant_id="t", review_id="r", candidate={}, extra="x")
