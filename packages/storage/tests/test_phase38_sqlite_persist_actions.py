from pathlib import Path

from crosswalk_review import ReviewActionType
from crosswalk_storage import SQLiteReviewRepository

from crosswalk_mapping import MappingCandidate, MappingStatus


def candidate() -> MappingCandidate:
    return MappingCandidate(
        external_path="$.id",
        canonical_path=None,
        score=0,
        status=MappingStatus.UNRESOLVED,
        evidence=None,
    )


def test_persist_actions(tmp_path: Path) -> None:
    from crosswalk_review import ReviewAction, ReviewRecord

    action = ReviewAction(
        version=1, action=ReviewActionType.REJECT, reviewer_id="a", rationale="no"
    )
    value = ReviewRecord(
        review_id="r", external_path="$.id", candidate=candidate(), version=1, actions=(action,)
    )
    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        repo.save("t", value, expected_version=None)
    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        assert repo.get("t", "r").actions[0].reviewer_id == "a"
