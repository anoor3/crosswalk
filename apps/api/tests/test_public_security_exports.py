from crosswalk_api import SECURITY_HEADERS


def test_security_headers_are_public() -> None:
    assert SECURITY_HEADERS["X-Frame-Options"] == "DENY"
