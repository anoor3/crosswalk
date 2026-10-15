from crosswalk_observability import Metric, sum_metrics


def test_metric_sum_filters_by_name() -> None:
    metrics = (
        Metric(name="jobs", value=2, unit="count"),
        Metric(name="jobs", value=3, unit="count"),
    )
    assert sum_metrics(metrics, "jobs") == 5
