from crosswalk_review import InMemoryReviewRepository
from crosswalk_service import ServiceContext

from crosswalk_mapping import MappingCandidate, MappingStatus


def candidate() -> MappingCandidate:
    return MappingCandidate(
        external_path="$.id",
        canonical_path=None,
        score=0,
        status=MappingStatus.UNRESOLVED,
        evidence=None,
    )


def test_context_injects_repository() -> None:
    repo = InMemoryReviewRepository()
    context = ServiceContext(review_repository=repo)
    context.reviews.open("t", "r", candidate())
    assert repo.get("t", "r").review_id == "r"
