from crosswalk_api import EventLog


def test_event_log_starts_empty() -> None:
    assert EventLog().snapshot() == ()
