import pytest
from pydantic import ValidationError
from crosswalk_contracts import EvaluationExampleResponse, OpenReviewRequest, ReviewDecisionRequest, ReviewResponse

def test_evaluation_response_is_frozen() -> None:
    value=EvaluationExampleResponse(external_path="$.id", canonical_path="claim.id", review_id="r", review_version=1, reviewer_id="a", rationale="x")
    with pytest.raises(ValidationError): value.rationale="y"
