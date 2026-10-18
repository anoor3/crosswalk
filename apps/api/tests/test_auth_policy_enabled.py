from crosswalk_api.auth import AuthPolicy


def test_enabled_auth_requires_nonempty_header() -> None:
    policy = AuthPolicy(enabled=True)

    assert not policy.accepts(None)
    assert not policy.accepts(" ")
