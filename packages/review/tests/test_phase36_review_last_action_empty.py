from crosswalk_review import ReviewWorkspace

from crosswalk_mapping import MappingCandidate, MappingStatus, canonical_fields


def candidate() -> MappingCandidate:
    return MappingCandidate(
        external_path="$.id",
        canonical_path=None,
        score=0,
        status=MappingStatus.UNRESOLVED,
        evidence=None,
    )


def test_last_action_empty() -> None:
    assert ReviewWorkspace(canonical_fields()).open("r", candidate()).last_action is None
