from crosswalk_api import Metrics


def test_metrics_tracks_names_independently() -> None:
    metrics = Metrics()
    metrics.increment("requests.total")
    metrics.increment("requests.errors")

    assert metrics.snapshot() == {"requests.total": 1, "requests.errors": 1}
