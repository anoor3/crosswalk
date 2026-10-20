from crosswalk_api import EventLog


def test_event_log_records_event() -> None:
    log = EventLog()
    log.record("startup")

    assert log.snapshot() == ({"event": "startup"},)
