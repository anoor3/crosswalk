import pytest
from pydantic import ValidationError
from crosswalk_contracts import EvaluationExampleResponse, OpenReviewRequest, ReviewDecisionRequest, ReviewResponse

def test_evaluation_requires_positive_version() -> None:
    with pytest.raises(ValidationError): EvaluationExampleResponse(external_path="$.id", canonical_path="claim.id", review_id="r", review_version=0, reviewer_id="a", rationale="x")
