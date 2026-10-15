import pytest
from crosswalk_security import UnsafeUrlError, validate_outbound_url


def test_public_https_url_is_allowed() -> None:
    assert validate_outbound_url("https://api.example.com/v1") == "https://api.example.com/v1"


@pytest.mark.parametrize(
    "value", ["file:///etc/passwd", "http://localhost:8080", "http://127.0.0.1"]
)
def test_local_or_non_http_urls_are_blocked(value: str) -> None:
    with pytest.raises(UnsafeUrlError):
        validate_outbound_url(value)
