from crosswalk_review import InMemoryReviewRepository
from crosswalk_service import ReviewRegistry

from crosswalk_mapping import MappingCandidate, MappingStatus


def candidate() -> MappingCandidate:
    return MappingCandidate(
        external_path="$.id",
        canonical_path=None,
        score=0,
        status=MappingStatus.UNRESOLVED,
        evidence=None,
    )


def test_record_count_after_two() -> None:
    repo = InMemoryReviewRepository()
    r = ReviewRegistry(repo)
    r.open("t", "a", candidate())
    r.open("t", "b", candidate())
    assert r.count("t") == 2
