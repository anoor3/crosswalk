from crosswalk_security import normalize_url


def test_normalize_url_removes_fragment_and_normalizes_host() -> None:
    assert normalize_url("HTTPS://API.Example.com/path#fragment") == "https://api.example.com/path"
