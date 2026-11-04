import pytest
from pydantic import ValidationError
from crosswalk_contracts import EvaluationExampleResponse, OpenReviewRequest, ReviewDecisionRequest, ReviewResponse

def test_review_response_accepts_zero_version() -> None:
    assert ReviewResponse(review_id="r", external_path="$.id", state="OPEN", version=0).version == 0
