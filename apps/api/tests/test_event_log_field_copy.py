from crosswalk_api import EventLog


def test_event_log_does_not_share_snapshot_dicts() -> None:
    log = EventLog()
    log.record("event", {"value": "one"})
    snapshot = log.snapshot()
    snapshot[0]["value"] = "changed"

    assert log.snapshot()[0]["value"] == "one"
