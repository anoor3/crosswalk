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


def test_summary_total() -> None:
    w = ReviewWorkspace(canonical_fields())
    w.open("r", candidate())
    s = w.summary()
    assert s.total == s.open + s.confirmed + s.corrected + s.rejected + s.unresolved
