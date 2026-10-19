from crosswalk_api import Metrics


def test_metrics_registry_increments_and_snapshots() -> None:
    metrics = Metrics()
    metrics.increment("requests.total")
    metrics.increment("requests.total")

    assert metrics.snapshot() == {"requests.total": 2}
