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


def test_update_version() -> None:
    repo = InMemoryReviewRepository()
    repo.save("t", record(), expected_version=None)
    updated = record()
    updated = updated.model_copy(update={"version": 1, "actions": ()})
    assert repo.save("t", updated, expected_version=0).version == 1
