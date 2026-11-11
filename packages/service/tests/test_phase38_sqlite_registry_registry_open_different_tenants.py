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


def test_registry_open_different_tenants(tmp_path: Path) -> None:
    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        r = ReviewRegistry(repo)
        r.open("a", "r", candidate())
        r.open("b", "r", candidate())
        assert len(repo.list("a")) == len(repo.list("b")) == 1
