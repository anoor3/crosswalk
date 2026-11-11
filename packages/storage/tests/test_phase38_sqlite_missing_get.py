from pathlib import Path

import pytest
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


def test_missing_get(tmp_path: Path) -> None:
    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo, pytest.raises(KeyError):
        repo.get("t", "missing")
