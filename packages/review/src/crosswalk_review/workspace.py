"""Small in-memory review service with optimistic concurrency.

The service intentionally has no HTTP or database dependency. Its interface is
the domain contract a later API/UI and durable repository can implement.
"""

from __future__ import annotations

from collections.abc import Iterable

from crosswalk_mapping import CanonicalField, MappingCandidate

from .errors import (
    DuplicateReviewError,
    InvalidReviewActionError,
    ReviewNotFoundError,
    StaleReviewError,
)
from .models import (
    EvaluationExample,
    ReviewAction,
    ReviewActionType,
    ReviewRecord,
    ReviewState,
)


class ReviewWorkspace:
    """Open, inspect, and decide mapping reviews in one process."""

    def __init__(self, targets: Iterable[CanonicalField]) -> None:
        target_paths = tuple(target.path for target in targets)
        if len(target_paths) != len(set(target_paths)):
            raise ValueError("duplicate canonical target paths")
        self._target_paths = frozenset(target_paths)
        self._records: dict[str, ReviewRecord] = {}

    def open(self, review_id: str, candidate: MappingCandidate) -> ReviewRecord:
        """Create an open review snapshot; IDs make retries safe and explicit."""
        if not review_id.strip():
            raise ValueError("review_id must not be blank")
        if review_id in self._records:
            raise DuplicateReviewError(f"review already exists: {review_id}")
        record = ReviewRecord(
            review_id=review_id,
            external_path=candidate.external_path,
            candidate=candidate,
        )
        self._records[review_id] = record
        return record

    def get(self, review_id: str) -> ReviewRecord:
        try:
            return self._records[review_id]
        except KeyError as error:
            raise ReviewNotFoundError(f"review not found: {review_id}") from error

    def list_open(self) -> tuple[ReviewRecord, ...]:
        return tuple(
            record for record in self._records.values() if record.state is ReviewState.OPEN
        )

    def decide(
        self,
        review_id: str,
        *,
        action: ReviewActionType,
        reviewer_id: str,
        expected_version: int,
        rationale: str,
        canonical_path: str | None = None,
    ) -> ReviewRecord:
        """Append a decision only when the caller has the current version."""
        current = self.get(review_id)
        if expected_version != current.version:
            raise StaleReviewError(
                f"review {review_id} is at version {current.version}, not {expected_version}"
            )
        if current.state is not ReviewState.OPEN:
            raise InvalidReviewActionError("a decided review cannot be decided again")
        if not reviewer_id.strip():
            raise InvalidReviewActionError("reviewer_id must not be blank")
        if not rationale.strip():
            raise InvalidReviewActionError("rationale must not be blank")
        if action in (ReviewActionType.CONFIRM, ReviewActionType.CORRECT):
            if canonical_path not in self._target_paths:
                raise InvalidReviewActionError("canonical target is not in the review vocabulary")
            if (
                action is ReviewActionType.CONFIRM
                and current.candidate.canonical_path != canonical_path
            ):
                raise InvalidReviewActionError(
                    "confirm must select the candidate target; use correct"
                )
            if (
                action is ReviewActionType.CORRECT
                and current.candidate.canonical_path == canonical_path
            ):
                raise InvalidReviewActionError("correct must change the candidate target")
        elif canonical_path is not None:
            raise InvalidReviewActionError("reject and leave-unresolved cannot select a target")

        new_version = current.version + 1
        decision = ReviewAction(
            version=new_version,
            action=action,
            reviewer_id=reviewer_id.strip(),
            canonical_path=canonical_path,
            rationale=rationale.strip(),
        )
        state = {
            ReviewActionType.CONFIRM: ReviewState.CONFIRMED,
            ReviewActionType.CORRECT: ReviewState.CORRECTED,
            ReviewActionType.REJECT: ReviewState.REJECTED,
            ReviewActionType.LEAVE_UNRESOLVED: ReviewState.UNRESOLVED,
        }[action]
        record = current.model_copy(
            update={
                "state": state,
                "canonical_path": canonical_path,
                "version": new_version,
                "actions": (*current.actions, decision),
            }
        )
        self._records[review_id] = record
        return record

    def evaluation_example(self, review_id: str) -> EvaluationExample | None:
        """Return only confirmed/corrected decisions as evaluation examples."""
        record = self.get(review_id)
        if record.state not in (ReviewState.CONFIRMED, ReviewState.CORRECTED):
            return None
        action = record.actions[-1]
        assert action.canonical_path is not None  # enforced by ReviewAction
        return EvaluationExample(
            external_path=record.external_path,
            canonical_path=action.canonical_path,
            review_id=record.review_id,
            review_version=record.version,
            reviewer_id=action.reviewer_id,
            rationale=action.rationale,
        )
