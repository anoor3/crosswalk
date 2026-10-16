from crosswalk_contracts import ErrorEnvelope


def test_error_envelope_has_stable_json_keys() -> None:
    payload = ErrorEnvelope(code="x", message="y", trace_id="z").model_dump(mode="json")
    assert list(payload) == ["code", "message", "trace_id"]
