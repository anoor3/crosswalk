from crosswalk_review import InMemoryReviewRepository, ReviewActionType
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


def test_rehydrate_history() -> None:
    repo = InMemoryReviewRepository()
    first = ReviewRegistry(repo)
    first.open("t", "r", candidate())
    first.decide(
        "t",
        "r",
        action=ReviewActionType.REJECT,
        reviewer_id="a",
        expected_version=0,
        rationale="no",
    )
    assert len(ReviewRegistry(repo).history("t", "r")) == 1
