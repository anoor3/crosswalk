from crosswalk_api.auth import AuthPolicy


def test_auth_policy_exposes_header_name() -> None:
    assert AuthPolicy().header_name == "Authorization"
