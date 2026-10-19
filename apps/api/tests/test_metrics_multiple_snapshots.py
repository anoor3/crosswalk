from crosswalk_api import Metrics


def test_metrics_snapshots_reflect_new_counts() -> None:
    metrics = Metrics()
    first = metrics.snapshot()
    metrics.increment("requests.total")

    assert first == {}
    assert metrics.snapshot() == {"requests.total": 1}
