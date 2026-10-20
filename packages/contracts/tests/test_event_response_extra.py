from crosswalk_contracts import EventResponse


def test_event_response_preserves_extra_fields() -> None:
    value = EventResponse(event="request.received", path="/health")

    assert value.model_dump()["path"] == "/health"
