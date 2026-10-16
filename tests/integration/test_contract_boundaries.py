from crosswalk_contracts import ErrorEnvelope, HealthResponse, Page


def test_shared_contracts_round_trip_across_boundaries() -> None:
    health = HealthResponse(status="ok", version="test")
    page = Page[dict[str, str]](items=({"status": health.status},))
    error = ErrorEnvelope(code="none", message="none", trace_id="trace")
    assert page.items[0]["status"] == "ok"
    assert error.trace_id == "trace"
