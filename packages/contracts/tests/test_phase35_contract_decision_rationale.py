import pytest
from pydantic import ValidationError
from crosswalk_contracts import EvaluationExampleResponse, OpenReviewRequest, ReviewDecisionRequest, ReviewResponse

def test_decision_rejects_empty_rationale() -> None:
    with pytest.raises(ValidationError): ReviewDecisionRequest(tenant_id="t", action="REJECT", reviewer_id="a", expected_version=0, rationale="")
