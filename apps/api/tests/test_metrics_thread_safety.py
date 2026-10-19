from concurrent.futures import ThreadPoolExecutor

from crosswalk_api import Metrics


def test_metrics_increment_is_thread_safe() -> None:
    metrics = Metrics()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: metrics.increment("requests.total"), range(20)))

    assert metrics.snapshot()["requests.total"] == 20
