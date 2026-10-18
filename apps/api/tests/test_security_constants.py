from crosswalk_api.security_headers import SECURITY_HEADERS


def test_security_headers_are_explicit() -> None:
    assert set(SECURITY_HEADERS) == {
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
    }
