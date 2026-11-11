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


def test_registry_rehydrates(tmp_path: Path) -> None:
    path = tmp_path / "reviews.db"
    with SQLiteReviewRepository(path) as repo:
        ReviewRegistry(repo).open("t", "r", candidate())
    with SQLiteReviewRepository(path) as repo:
        assert ReviewRegistry(repo).get("t", "r").review_id == "r"
