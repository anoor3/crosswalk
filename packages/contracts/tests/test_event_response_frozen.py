import pytest
from crosswalk_contracts import EventResponse
from pydantic import ValidationError


def test_event_response_is_frozen() -> None:
    value = EventResponse(event="request.received")
    with pytest.raises(ValidationError):
        value.event = "changed"  # type: ignore[misc]
