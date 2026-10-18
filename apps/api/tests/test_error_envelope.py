from crosswalk_contracts import ErrorEnvelope


def test_error_envelope_serializes() -> None:
    value = ErrorEnvelope(code="bad", message="invalid", trace_id="t1")

    assert value.model_dump() == {"code": "bad", "message": "invalid", "trace_id": "t1"}
