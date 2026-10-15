from crosswalk_observability import Event, Metric, new_trace_id


def test_trace_ids_are_unique_and_events_are_structured() -> None:
    first = new_trace_id()
    second = new_trace_id()
    assert first != second
    event = Event(name="job.started", trace_id=first, occurred_at="2026-01-01T00:00:00Z")
    metric = Metric(name="job.duration", value=1.5, unit="seconds")
    assert event.trace_id == first
    assert metric.unit == "seconds"
