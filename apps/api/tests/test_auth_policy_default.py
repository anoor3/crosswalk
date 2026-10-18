from crosswalk_api.auth import AuthPolicy


def test_auth_policy_defaults_to_disabled() -> None:
    assert AuthPolicy().accepts(None)
