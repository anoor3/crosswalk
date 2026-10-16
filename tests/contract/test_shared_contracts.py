from crosswalk_contracts import ErrorEnvelope, HealthResponse, Page


def test_contracts_emit_json_safe_values() -> None:
    payload = {
        "health": HealthResponse(status="ok", version="v").model_dump(mode="json"),
        "page": Page[str](items=("a",)).model_dump(mode="json"),
        "error": ErrorEnvelope(code="x", message="y", trace_id="z").model_dump(mode="json"),
    }
    assert payload["page"]["items"] == ["a"]
