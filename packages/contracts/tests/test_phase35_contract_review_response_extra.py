import pytest
from pydantic import ValidationError
from crosswalk_contracts import EvaluationExampleResponse, OpenReviewRequest, ReviewDecisionRequest, ReviewResponse

def test_review_response_rejects_extra() -> None:
    with pytest.raises(ValidationError): ReviewResponse(review_id="r", external_path="$.id", state="OPEN", version=0, extra="x")
