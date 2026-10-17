from crosswalk_api.request_id import request_trace_id


def test_request_trace_id_preserves_safe_header_or_generates_one() -> None:
    assert request_trace_id("trace-1") == "trace-1"
    assert len(request_trace_id(None)) == 32
