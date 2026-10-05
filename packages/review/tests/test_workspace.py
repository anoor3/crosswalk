"""State-machine and audit guarantees for Phase 5 review."""

import pytest
from crosswalk_review import (
    DuplicateReviewError,
    InvalidReviewActionError,
    ReviewAction,
    ReviewActionType,
    ReviewNotFoundError,
    ReviewState,
    ReviewWorkspace,
    StaleReviewError,
)
from pydantic import ValidationError

from crosswalk_discovery import ExternalField, FieldType
from crosswalk_mapping import CanonicalField, MappingCandidate, MappingStatus, map_fields


def target(path: str = "claim.claim_id") -> CanonicalField:
    return CanonicalField(path=path, name=path.rsplit(".", 1)[-1], data_type=FieldType.STRING)


def candidate() -> MappingCandidate:
    return map_fields(
        [
            ExternalField(
                json_path="$.claimNumber",
                name="claimNumber",
                data_type=FieldType.STRING,
                required=True,
            )
        ],
        targets=[target()],
    )[0]


def workspace() -> ReviewWorkspace:
    return ReviewWorkspace([target(), target("claim.policy.policy_number")])


def test_open_and_confirm_creates_versioned_evaluation_example() -> None:
    reviews = workspace()
    opened = reviews.open("review-1", candidate())
    assert opened.state is ReviewState.OPEN
    assert opened.version == 0
    assert reviews.list_open() == (opened,)

    decided = reviews.decide(
        "review-1",
        action=ReviewActionType.CONFIRM,
        reviewer_id="alice",
        expected_version=0,
        rationale="The source name and compatible string type identify the claim ID.",
        canonical_path="claim.claim_id",
    )
    assert decided.state is ReviewState.CONFIRMED
    assert decided.version == 1
    assert decided.actions[0].version == 1
    assert reviews.list_open() == ()
    example = reviews.evaluation_example("review-1")
    assert example is not None
    assert example.canonical_path == "claim.claim_id"
    assert example.review_version == 1
    assert "source name" in example.rationale


def test_correct_requires_different_target_and_is_auditable() -> None:
    reviews = workspace()
    reviews.open("review-2", candidate())
    corrected = reviews.decide(
        "review-2",
        action=ReviewActionType.CORRECT,
        reviewer_id="bob",
        expected_version=0,
        rationale="The source is the policy number after reviewing the API documentation.",
        canonical_path="claim.policy.policy_number",
    )
    assert corrected.state is ReviewState.CORRECTED
    assert corrected.canonical_path == "claim.policy.policy_number"
    example = reviews.evaluation_example("review-2")
    assert example is not None
    assert example.reviewer_id == "bob"

    with pytest.raises(InvalidReviewActionError, match="cannot be decided again"):
        reviews.decide(
            "review-2",
            action=ReviewActionType.REJECT,
            reviewer_id="bob",
            expected_version=1,
            rationale="second decision",
        )


@pytest.mark.parametrize("action", [ReviewActionType.REJECT, ReviewActionType.LEAVE_UNRESOLVED])
def test_non_approving_actions_have_no_target_and_no_evaluation_example(
    action: ReviewActionType,
) -> None:
    reviews = workspace()
    reviews.open(f"{action.value}-review", candidate())
    record = reviews.decide(
        f"{action.value}-review",
        action=action,
        reviewer_id="reviewer",
        expected_version=0,
        rationale="The evidence is insufficient to approve this mapping.",
    )
    assert record.state is (
        ReviewState.REJECTED if action is ReviewActionType.REJECT else ReviewState.UNRESOLVED
    )
    assert record.canonical_path is None
    assert reviews.evaluation_example(record.review_id) is None


def test_stale_update_is_rejected_without_mutating_record() -> None:
    reviews = workspace()
    opened = reviews.open("concurrent", candidate())
    current = reviews.decide(
        "concurrent",
        action=ReviewActionType.CONFIRM,
        reviewer_id="first",
        expected_version=opened.version,
        rationale="Confirmed from source documentation.",
        canonical_path="claim.claim_id",
    )
    with pytest.raises(StaleReviewError):
        reviews.decide(
            "concurrent",
            action=ReviewActionType.REJECT,
            reviewer_id="second",
            expected_version=opened.version,
            rationale="Stale reviewer decision.",
        )
    assert reviews.get("concurrent") == current


def test_duplicate_and_missing_reviews_are_typed_errors() -> None:
    reviews = workspace()
    reviews.open("same", candidate())
    with pytest.raises(DuplicateReviewError):
        reviews.open("same", candidate())
    with pytest.raises(ReviewNotFoundError):
        reviews.get("missing")


@pytest.mark.parametrize(
    ("action", "canonical_path", "message"),
    [
        (ReviewActionType.CONFIRM, "claim.policy.policy_number", "confirm"),
        (ReviewActionType.CORRECT, "unknown.target", "vocabulary"),
        (ReviewActionType.REJECT, "claim.claim_id", "cannot select"),
        (ReviewActionType.LEAVE_UNRESOLVED, "claim.claim_id", "cannot select"),
    ],
)
def test_invalid_decisions_do_not_change_open_review(
    action: ReviewActionType, canonical_path: str | None, message: str
) -> None:
    reviews = workspace()
    reviews.open("invalid", candidate())
    with pytest.raises(InvalidReviewActionError, match=message):
        reviews.decide(
            "invalid",
            action=action,
            reviewer_id="reviewer",
            expected_version=0,
            rationale="Attempted invalid transition.",
            canonical_path=canonical_path,
        )
    assert reviews.get("invalid").state is ReviewState.OPEN


def test_action_model_requires_target_only_for_approvals() -> None:
    with pytest.raises(ValidationError):
        ReviewAction(
            version=1,
            action=ReviewActionType.CONFIRM,
            reviewer_id="reviewer",
            rationale="missing target",
        )
    with pytest.raises(ValidationError):
        ReviewAction(
            version=1,
            action=ReviewActionType.REJECT,
            reviewer_id="reviewer",
            canonical_path="claim.claim_id",
            rationale="reject with target",
        )


def test_candidate_status_is_preserved_until_human_decision() -> None:
    record = workspace().open("status", candidate())
    assert record.candidate.status in (MappingStatus.HIGH_CONFIDENCE, MappingStatus.REVIEW_REQUIRED)
    assert record.state is ReviewState.OPEN
