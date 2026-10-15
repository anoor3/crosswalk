from __future__ import annotations

from .events import Event, Metric


class InMemorySink:
    """Testable sink boundary; production exporters can implement the same methods."""

    def __init__(self) -> None:
        self.events: list[Event] = []
        self.metrics: list[Metric] = []

    def record_event(self, item: Event) -> None:
        self.events.append(item)

    def record_metric(self, item: Metric) -> None:
        self.metrics.append(item)
