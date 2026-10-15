from crosswalk_repair import RepairProposal, RepairStatus

from crosswalk_drift import DriftEvent, DriftKind


def test_proposals_require_explicit_approval() -> None:
    proposal = RepairProposal(
        drift=DriftEvent(kind=DriftKind.REMOVED_FIELD, path="lossDt"),
        replacement_path="loss_date",
        confidence=0.9,
        evidence=("same declared type",),
    )
    assert proposal.status is RepairStatus.PROPOSED
    assert proposal.approve().status is RepairStatus.APPROVED
