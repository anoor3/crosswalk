from crosswalk_agents import redact_summary


def test_redact_summary_removes_common_credentials() -> None:
    value = "api_key=abc123 authorization=Bearer secret-token field=customer_id"
    redacted = redact_summary(value)
    assert "abc123" not in redacted
    assert "Bearer" not in redacted
    assert "secret-token" not in redacted
    assert "customer_id" in redacted
