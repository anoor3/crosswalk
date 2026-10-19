from crosswalk_api import Metrics


def test_metrics_does_not_create_zero_counters() -> None:
    assert Metrics().snapshot() == {}
