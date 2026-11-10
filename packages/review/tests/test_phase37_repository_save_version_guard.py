from crosswalk_review import InMemoryReviewRepository, ReviewRecord

from crosswalk_mapping import MappingCandidate, MappingStatus


def record(review_id: str = "r1") -> ReviewRecord:
    return ReviewRecord(
        review_id=review_id,
        external_path="$.id",
        candidate=MappingCandidate(
            external_path="$.id",
            canonical_path=None,
            score=0,
            status=MappingStatus.UNRESOLVED,
            evidence=None,
        ),
    )


import pytest  # noqa: E402
from crosswalk_review import ReviewRepositoryConflict  # noqa: E402


def test_save_version_guard() -> None:
    repo = InMemoryReviewRepository()
    repo.save("t", record(), expected_version=None)
    with pytest.raises(ReviewRepositoryConflict):
        repo.save("t", record().model_copy(update={"version": 1}), expected_version=2)
