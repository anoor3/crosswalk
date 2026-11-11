from pathlib import Path

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


def test_registry_record_candidate(tmp_path: Path) -> None:
    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        ReviewRegistry(repo).open("t", "r", candidate())
        assert repo.get("t", "r").candidate.status is MappingStatus.UNRESOLVED
