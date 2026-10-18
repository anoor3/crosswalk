from crosswalk_api.cors import CorsPolicy


def test_empty_cors_policy_rejects_origin() -> None:
    assert not CorsPolicy().allows("https://example.com")
