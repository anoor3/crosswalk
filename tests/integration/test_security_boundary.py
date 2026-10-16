from crosswalk_security import redact_audit_text, validate_outbound_url


def test_security_boundary_keeps_public_url_and_redacts_text() -> None:
    assert validate_outbound_url("https://example.com") == "https://example.com"
    assert "hidden" not in redact_audit_text("secret=hidden")
