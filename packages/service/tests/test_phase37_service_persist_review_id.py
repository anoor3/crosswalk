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


def test_persist_review_id() -> None:
    repo = InMemoryReviewRepository()
    ReviewRegistry(repo).open("t", "r", candidate())
    assert repo.get("t", "r").review_id == "r"
