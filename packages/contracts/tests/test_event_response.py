from crosswalk_contracts import EventResponse


def test_event_response_serializes() -> None:
    value = EventResponse(event="request.received", path="/health")

    assert value.event == "request.received"
    assert value.path == "/health"
