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


def test_list_does_not_cross() -> None:
    repo = InMemoryReviewRepository()
    repo.save("a", record("a"), expected_version=None)
    repo.save("b", record("b"), expected_version=None)
    assert [r.review_id for r in repo.list("a")] == ["a"]
