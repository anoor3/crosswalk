from crosswalk_api import EventLog


def test_event_log_preserves_order() -> None:
    log = EventLog()
    log.record("first")
    log.record("second")

    assert [event["event"] for event in log.snapshot()] == ["first", "second"]
