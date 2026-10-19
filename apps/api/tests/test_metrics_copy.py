from crosswalk_api import Metrics


def test_metrics_snapshot_is_copy() -> None:
    metrics = Metrics()
    snapshot = metrics.snapshot()
    snapshot["requests.total"] = 99

    assert metrics.snapshot() == {}
