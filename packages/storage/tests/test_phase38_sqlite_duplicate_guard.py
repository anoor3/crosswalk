from pathlib import Path

import pytest
from crosswalk_review import ReviewRepositoryConflict
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


def test_duplicate_guard(tmp_path: Path) -> None:
    from crosswalk_review import ReviewRecord

    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        value = ReviewRecord(review_id="r", external_path="$.id", candidate=candidate())
        repo.save("t", value, expected_version=None)
        with pytest.raises(ReviewRepositoryConflict):
            repo.save("t", value, expected_version=None)
