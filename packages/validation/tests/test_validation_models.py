from datetime import UTC, datetime

from crosswalk_validation import Feedback, FeedbackKind, ValidationSession


def test_validation_feedback_is_append_only() -> None:
    session = ValidationSession(
        id="s1", tenant_id="t1", reviewer_id="r1", started_at=datetime.now(UTC)
    )
    updated = session.add_feedback(Feedback(field_path="claim.id", kind=FeedbackKind.CORRECT))
    assert session.feedback == ()
    assert updated.feedback[0].field_path == "claim.id"
