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


def test_unknown_action() -> None:
    assert ReviewWorkspace(canonical_fields()).list_by_action(ReviewActionType.CONFIRM) == ()
