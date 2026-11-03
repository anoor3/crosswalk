import pytest
from crosswalk_discovery import ExternalField, FieldType
from crosswalk_mapping import CanonicalField, MappingCandidate, MappingStatus, map_fields
from crosswalk_review import ReviewActionType, ReviewWorkspace


def target(path: str = "claim.claim_id") -> CanonicalField:
    return CanonicalField(path=path, name=path.rsplit(".", 1)[-1], data_type=FieldType.STRING)


def candidate() -> MappingCandidate:
    return map_fields([ExternalField(json_path="$.claimNumber", name="claimNumber", data_type=FieldType.STRING, required=True)], targets=[target()])[0]


def workspace() -> ReviewWorkspace:
    return ReviewWorkspace([target(), target("claim.policy.policy_number")])

def test_reject_sets_rejected_state() -> None:
    reviews=workspace(); reviews.open("r1", candidate()); record=reviews.decide("r1", action=ReviewActionType.REJECT, reviewer_id="a", expected_version=0, rationale="No match")
    assert record.state.value == "REJECTED"
