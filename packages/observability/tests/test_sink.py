from crosswalk_observability import Event, InMemorySink, Metric


def test_memory_sink_preserves_event_and_metric_order() -> None:
    sink = InMemorySink()
    sink.record_event(Event(name="started", trace_id="t", occurred_at="2026-01-01T00:00:00Z"))
    sink.record_metric(Metric(name="duration", value=1, unit="s"))
    assert [item.name for item in sink.events] == ["started"]
    assert [item.name for item in sink.metrics] == ["duration"]
