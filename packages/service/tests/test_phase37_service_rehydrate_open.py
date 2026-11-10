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


def test_rehydrate_open() -> None:
    repo = InMemoryReviewRepository()
    first = ReviewRegistry(repo)
    first.open("t", "r", candidate())
    assert ReviewRegistry(repo).get("t", "r").review_id == "r"
