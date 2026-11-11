from pathlib import Path

from crosswalk_review import ReviewActionType
from crosswalk_service import ReviewRegistry
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


def test_registry_history_after_restart(tmp_path: Path) -> None:
    path = tmp_path / "reviews.db"
    with SQLiteReviewRepository(path) as repo:
        r = ReviewRegistry(repo)
        r.open("t", "r", candidate())
        r.decide(
            "t",
            "r",
            action=ReviewActionType.REJECT,
            reviewer_id="a",
            expected_version=0,
            rationale="no",
        )
    with SQLiteReviewRepository(path) as repo:
        assert len(ReviewRegistry(repo).history("t", "r")) == 1
