from concurrent.futures import ThreadPoolExecutor

from crosswalk_api import EventLog


def test_event_log_is_thread_safe() -> None:
    log = EventLog()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: log.record("tick"), range(20)))

    assert len(log.snapshot()) == 20
