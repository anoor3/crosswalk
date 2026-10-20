import pytest
from crosswalk_contracts import EventResponse
from pydantic import ValidationError


def test_event_response_requires_event() -> None:
    with pytest.raises(ValidationError):
        EventResponse(event="")
