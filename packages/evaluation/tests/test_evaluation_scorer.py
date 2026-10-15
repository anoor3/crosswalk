import pytest
from crosswalk_evaluation import evaluate_candidates


def test_empty_evaluation_is_explicit_and_zeroed() -> None:
    report = evaluate_candidates((), {})
    assert report.total == 0
    assert report.accuracy == 0


def test_expected_key_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="expected keys"):
        evaluate_candidates((), {"missing": "claim.id"})
