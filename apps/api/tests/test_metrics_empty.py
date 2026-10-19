from crosswalk_api import Metrics


def test_metrics_snapshot_starts_empty() -> None:
    assert Metrics().snapshot() == {}
