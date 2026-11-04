import pytest
from pydantic import ValidationError
from crosswalk_contracts import EvaluationExampleResponse, OpenReviewRequest, ReviewDecisionRequest, ReviewResponse

def test_open_review_requires_tenant() -> None:
    with pytest.raises(ValidationError): OpenReviewRequest(tenant_id="", review_id="r", candidate={})
