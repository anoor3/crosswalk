from crosswalk_api import EventLog


def test_event_log_records_fields() -> None:
    log = EventLog()
    log.record("request", {"path": "/health"})

    assert log.snapshot() == ({"event": "request", "path": "/health"},)
