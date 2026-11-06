from crosswalk_review import ReviewState, ReviewWorkspace

from crosswalk_mapping import MappingCandidate, MappingStatus, canonical_fields


def candidate() -> MappingCandidate:
    return MappingCandidate(
        external_path="$.id",
        canonical_path=None,
        score=0,
        status=MappingStatus.UNRESOLVED,
        evidence=None,
    )


def test_state_filter() -> None:
    w = ReviewWorkspace(canonical_fields())
    w.open("r", candidate())
    assert len(w.list_by_state(ReviewState.OPEN)) == 1
