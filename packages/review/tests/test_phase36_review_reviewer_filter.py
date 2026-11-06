from crosswalk_review import ReviewActionType, ReviewWorkspace

from crosswalk_mapping import MappingCandidate, MappingStatus, canonical_fields


def candidate() -> MappingCandidate:
    return MappingCandidate(
        external_path="$.id",
        canonical_path=None,
        score=0,
        status=MappingStatus.UNRESOLVED,
        evidence=None,
    )


def test_reviewer_filter() -> None:
    w = ReviewWorkspace(canonical_fields())
    w.open("r", candidate())
    w.decide(
        "r", action=ReviewActionType.REJECT, reviewer_id="a", expected_version=0, rationale="no"
    )
    assert len(w.list_by_reviewer("a")) == 1
