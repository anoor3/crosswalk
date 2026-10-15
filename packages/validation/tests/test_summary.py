from crosswalk_validation import Feedback, FeedbackKind, summarize_feedback


def test_feedback_summary_includes_zero_categories() -> None:
    result = summarize_feedback((Feedback(field_path="id", kind=FeedbackKind.CORRECT),))
    assert result == {"CORRECT": 1, "INCORRECT": 0, "UNCLEAR": 0, "MISSING": 0}
