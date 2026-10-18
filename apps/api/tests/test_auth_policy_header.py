from crosswalk_api.auth import AuthPolicy


def test_auth_accepts_nonempty_header() -> None:
    assert AuthPolicy(enabled=True).accepts("Bearer token")
