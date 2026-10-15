"""Relationship scoring, ranking, and graph safety tests."""

import pytest
from crosswalk_relationships import (
    Cardinality,
    DuplicateRelationshipError,
    FieldReference,
    RelationshipEdge,
    RelationshipGraph,
    RelationshipNode,
    RelationshipStatus,
    rank_relationships,
    score_relationship,
)


def ref(endpoint: str, path: str, name: str, data_type: str = "string") -> FieldReference:
    return FieldReference(endpoint=endpoint, json_path=path, name=name, data_type=data_type)


def test_strong_overlap_is_high_confidence() -> None:
    candidate = score_relationship(
        ref("claims", "$.personId", "personId"),
        ref("people", "$.personId", "personId"),
        ["p1", "p2"],
        ["p1", "p2", "p2"],
    )
    assert candidate.status is RelationshipStatus.HIGH_CONFIDENCE
    assert candidate.cardinality is Cardinality.ONE_TO_MANY
    assert candidate.evidence is not None
    assert candidate.evidence.overlap_count == 2


def test_no_overlap_is_unresolved_and_has_no_target() -> None:
    candidate = score_relationship(
        ref("claims", "$.claimantId", "claimantId"),
        ref("people", "$.personId", "personId"),
        ["p1"],
        ["x1"],
    )
    assert candidate.status is RelationshipStatus.UNRESOLVED
    assert candidate.target is None


def test_close_targets_become_conflicting_with_alternatives() -> None:
    source = ref("claims", "$.ownerId", "ownerId")
    targets = [ref("people", "$.id", "id"), ref("accounts", "$.id", "id")]
    result = rank_relationships(
        source,
        targets,
        ["1", "2"],
        {("people", "$.id"): ["1", "2"], ("accounts", "$.id"): ["1", "2"]},
    )
    assert result.status is RelationshipStatus.CONFLICTING
    assert len(result.alternatives) == 1


def test_missing_target_samples_are_rejected() -> None:
    with pytest.raises(ValueError, match="missing"):
        rank_relationships(
            ref("claims", "$.ownerId", "ownerId"),
            [ref("people", "$.id", "id")],
            ["1"],
            {},
        )


def test_duplicate_targets_are_rejected() -> None:
    target = ref("people", "$.id", "id")
    with pytest.raises(DuplicateRelationshipError):
        rank_relationships(target, [target, target], ["1"], {("people", "$.id"): ["1"]})


def test_graph_references_are_validated_and_cycles_are_explicit() -> None:
    graph = RelationshipGraph(
        nodes=(RelationshipNode(endpoint="claims"), RelationshipNode(endpoint="people")),
        edges=(
            RelationshipEdge(
                source_endpoint="claims",
                target_endpoint="people",
                source_path="$.claimantId",
                target_path="$.id",
                status=RelationshipStatus.HIGH_CONFIDENCE,
                cardinality=Cardinality.MANY_TO_ONE,
                confidence=0.9,
            ),
            RelationshipEdge(
                source_endpoint="people",
                target_endpoint="claims",
                source_path="$.claimId",
                target_path="$.id",
                status=RelationshipStatus.REVIEW_REQUIRED,
                cardinality=Cardinality.MANY_TO_ONE,
                confidence=0.5,
            ),
        ),
    )
    assert graph.has_cycle()


def test_graph_rejects_unknown_nodes() -> None:
    with pytest.raises(ValueError, match="reference graph nodes"):
        RelationshipGraph(
            nodes=(RelationshipNode(endpoint="claims"),),
            edges=(
                RelationshipEdge(
                    source_endpoint="claims",
                    target_endpoint="people",
                    source_path="$.id",
                    target_path="$.id",
                    status=RelationshipStatus.REVIEW_REQUIRED,
                    cardinality=Cardinality.UNKNOWN,
                    confidence=0.2,
                ),
            ),
        )


def test_graph_json_roundtrip() -> None:
    graph = RelationshipGraph(nodes=(RelationshipNode(endpoint="claims"),))
    assert RelationshipGraph.model_validate_json(graph.model_dump_json()) == graph
