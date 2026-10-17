from crosswalk_api import CorsPolicy


def test_cors_policy_requires_explicit_origins() -> None:
    policy = CorsPolicy(allowed_origins=("https://example.com",))
    assert policy.allows("https://example.com")
    assert not policy.allows("https://other.example")
