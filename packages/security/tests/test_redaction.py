from crosswalk_security import redact_audit_text


def test_audit_redaction_removes_secret_values() -> None:
    result = redact_audit_text("token=abc123 field=claim.id")
    assert "abc123" not in result
    assert "claim.id" in result
