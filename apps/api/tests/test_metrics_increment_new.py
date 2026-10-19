from crosswalk_api import Metrics


def test_metrics_increment_creates_counter() -> None:
    metrics = Metrics()
    metrics.increment("custom.counter")

    assert metrics.snapshot()["custom.counter"] == 1
