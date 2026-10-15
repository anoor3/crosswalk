from collections.abc import Sequence

from .events import Metric


def sum_metrics(metrics: Sequence[Metric], name: str) -> float:
    return sum(metric.value for metric in metrics if metric.name == name)
