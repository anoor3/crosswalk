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


def test_rehydrate_reviewer() -> None:
    repo = InMemoryReviewRepository()
    r = ReviewRegistry(repo)
    r.open("t", "r", candidate())
    r.decide(
        "t",
        "r",
        action=ReviewActionType.REJECT,
        reviewer_id="a",
        expected_version=0,
        rationale="no",
    )
    assert len(ReviewRegistry(repo).list_by_reviewer("t", "a")) == 1
