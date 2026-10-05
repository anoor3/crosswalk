"""Reject misleading scores and incoherent mapping result states."""

import pytest
from pydantic import ValidationError

from crosswalk_mapping import (
    MappingAlternative,
    MappingCandidate,
    MappingEvidence,
    MappingStatus,
    SignalEvidence,
)


def evidence() -> MappingEvidence:
    return MappingEvidence(
        name=SignalEvidence(score=1, weight=0.45, reason="exact tokens"),
        description=SignalEvidence(score=None, weight=0.25, reason="absent"),
        type=SignalEvidence(score=1, weight=0.15, reason="compatible"),
        value_profile=SignalEvidence(score=0, weight=0.15, reason="incompatible"),
    )


def test_available_evidence_denominator() -> None:
    assert evidence().score == pytest.approx(0.8)


@pytest.mark.parametrize("score", [-0.01, 1.01, float("nan"), float("inf")])
def test_invalid_signal_score(score: float) -> None:
    with pytest.raises(ValidationError):
        SignalEvidence(score=score, weight=0.1, reason="invalid")


def test_fabricated_score_rejected() -> None:
    with pytest.raises(ValidationError, match="weighted evidence"):
        MappingAlternative(canonical_path="claim.id", score=0.99, evidence=evidence())


def test_unresolved_cannot_select_target() -> None:
    with pytest.raises(ValidationError, match="UNRESOLVED"):
        MappingCandidate(
            external_path="$.id",
            canonical_path="claim.id",
            score=evidence().score,
            status=MappingStatus.UNRESOLVED,
            evidence=evidence(),
        )


def test_json_roundtrip_and_immutable_result() -> None:
    result = MappingCandidate(
        external_path="$.id",
        canonical_path="claim.id",
        score=evidence().score,
        status=MappingStatus.REVIEW_REQUIRED,
        evidence=evidence(),
    )
    assert MappingCandidate.model_validate_json(result.model_dump_json()) == result
    with pytest.raises(ValidationError):
        result.score = 0.99
