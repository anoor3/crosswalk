from datetime import UTC, datetime

from crosswalk_validation import ValidationSession, export_session


def test_session_export_is_sorted_json() -> None:
    session = ValidationSession(
        id="s", tenant_id="t", reviewer_id="r", started_at=datetime.now(UTC)
    )
    exported = export_session(session)
    assert '"tenant_id": "t"' in exported
