from crosswalk_api.cors import CorsPolicy


def test_cors_policy_matches_allowlist() -> None:
    policy = CorsPolicy(allowed_origins=("https://example.com",))

    assert policy.allows("https://example.com")
    assert not policy.allows("https://other.example")
