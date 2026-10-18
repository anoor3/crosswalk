from crosswalk_api import MAX_REQUEST_BYTES


def test_request_limit_is_public() -> None:
    assert MAX_REQUEST_BYTES == 1_048_576
