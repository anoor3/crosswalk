from crosswalk_api import EventLog


def test_event_log_snapshot_copies_fields() -> None:
    fields = {"path": "/health"}
    log = EventLog()
    log.record("request", fields)
    fields["path"] = "/changed"

    assert log.snapshot()[0]["path"] == "/health"
