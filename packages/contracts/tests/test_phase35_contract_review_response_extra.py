import pytest
from crosswalk_contracts import (
    ReviewResponse,
)
from pydantic import ValidationError


def test_review_response_rejects_extra() -> None:
    with pytest.raises(ValidationError):
        ReviewResponse(  # type: ignore[call-arg]
            review_id="r", external_path="$.id", state="OPEN", version=0, extra="x"
        )
