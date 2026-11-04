import pytest
from pydantic import ValidationError
from crosswalk_contracts import EvaluationExampleResponse, OpenReviewRequest, ReviewDecisionRequest, ReviewResponse

def test_open_review_requires_review_id() -> None:
    with pytest.raises(ValidationError): OpenReviewRequest(tenant_id="t", review_id="", candidate={})
