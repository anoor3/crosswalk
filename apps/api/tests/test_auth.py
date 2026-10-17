from crosswalk_api import AuthPolicy


def test_auth_policy_is_off_by_default_and_checks_enabled_headers() -> None:
    assert AuthPolicy().accepts(None)
    assert not AuthPolicy(enabled=True).accepts(None)
    assert AuthPolicy(enabled=True).accepts("Bearer token")
