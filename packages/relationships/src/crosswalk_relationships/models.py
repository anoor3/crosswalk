"""Immutable relationship hypotheses and graph primitives."""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_CONFIG = ConfigDict(frozen=True, extra="forbid")


class RelationshipStatus(StrEnum):
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNRESOLVED = "UNRESOLVED"
    CONFLICTING = "CONFLICTING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class Cardinality(StrEnum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
    UNKNOWN = "unknown"


class FieldReference(BaseModel):
    model_config = _CONFIG

    endpoint: str = Field(min_length=1)
    json_path: str = Field(min_length=1)
    name: str = Field(min_length=1)
    data_type: str | None = None


class RelationshipEvidence(BaseModel):
    model_config = _CONFIG

    source_count: int = Field(ge=0)
    target_count: int = Field(ge=0)
    overlap_count: int = Field(ge=0)
    overlap_rate: float = Field(ge=0, le=1)
    source_unique_rate: float = Field(ge=0, le=1)
    target_unique_rate: float = Field(ge=0, le=1)
    name_score: float = Field(ge=0, le=1)
    type_score: float = Field(ge=0, le=1)
    reasons: tuple[str, ...] = ()


class RelationshipAlternative(BaseModel):
    model_config = _CONFIG

    target: FieldReference
    score: float = Field(ge=0, le=1)
    evidence: RelationshipEvidence


class RelationshipCandidate(BaseModel):
    model_config = _CONFIG

    source: FieldReference
    target: FieldReference | None
    score: float = Field(ge=0, le=1)
    status: RelationshipStatus
    cardinality: Cardinality
    evidence: RelationshipEvidence | None
    alternatives: tuple[RelationshipAlternative, ...] = ()

    @model_validator(mode="after")
    def _consistent(self) -> Self:
        if self.target is None and self.status is not RelationshipStatus.UNRESOLVED:
            raise ValueError("only unresolved relationships may omit a target")
        if self.target is not None and self.evidence is None:
            raise ValueError("a target requires evidence")
        if self.target in tuple(item.target for item in self.alternatives):
            raise ValueError("alternatives cannot include the selected target")
        return self


class RelationshipNode(BaseModel):
    model_config = _CONFIG

    endpoint: str = Field(min_length=1)


class RelationshipEdge(BaseModel):
    model_config = _CONFIG

    source_endpoint: str = Field(min_length=1)
    target_endpoint: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    target_path: str = Field(min_length=1)
    status: RelationshipStatus
    cardinality: Cardinality
    confidence: float = Field(ge=0, le=1)


class RelationshipGraph(BaseModel):
    model_config = _CONFIG

    nodes: tuple[RelationshipNode, ...] = ()
    edges: tuple[RelationshipEdge, ...] = ()

    @model_validator(mode="after")
    def _valid_edges(self) -> Self:
        endpoints = {node.endpoint for node in self.nodes}
        if len(endpoints) != len(self.nodes):
            raise ValueError("relationship nodes must be unique")
        if any(
            edge.source_endpoint not in endpoints or edge.target_endpoint not in endpoints
            for edge in self.edges
        ):
            raise ValueError("relationship edges must reference graph nodes")
        return self
