from pathlib import Path

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


def test_migration_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "reviews.db"
    with SQLiteReviewRepository(path) as first:
        assert first.migration_version() == 1
    with SQLiteReviewRepository(path) as second:
        assert second.migration_version() == 1
