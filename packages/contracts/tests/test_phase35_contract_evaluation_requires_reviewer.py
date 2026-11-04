import pytest
from crosswalk_contracts import (
    EvaluationExampleResponse,
)
from pydantic import ValidationError


def test_evaluation_requires_reviewer() -> None:
    with pytest.raises(ValidationError):
        EvaluationExampleResponse(
            external_path="$.id",
            canonical_path="claim.id",
            review_id="r",
            review_version=1,
            reviewer_id="",
            rationale="x",
        )
