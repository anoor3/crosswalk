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


def test_repository_property() -> None:
    repo = InMemoryReviewRepository()
    registry = ReviewRegistry(repo)
    assert registry.repository is repo
