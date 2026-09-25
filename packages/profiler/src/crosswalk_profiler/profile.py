"""The per-field statistical profile produced from observed sample values.

A :class:`FieldProfile` summarizes what a field *actually looks like* in real
data, addressed by its ``json_path``. It is computed deterministically from
sample payloads — no inference, no LLM (PLANNER §16, CHECKER §15) — and is one
of the strongest evidence signals the later mapping phase will consume.

Privacy note (CHECKER §15): profiles keep only a small, capped set of example
values and aggregate statistics. They are designed so that logging or storing a
profile does not dump an entire dataset of potentially sensitive payloads.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

_MODEL_CONFIG = ConfigDict(frozen=True, extra="forbid")


class ObservedType(StrEnum):
    """A JSON value's runtime type, as observed in samples."""

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"


class SemanticType(StrEnum):
    """A heuristic guess at what a field *means*, from its values alone.

    These are deterministic heuristics (regex/statistics), not AI judgments.
    They are hints for the mapping phase, always accompanied by the raw stats
    that produced them so a reviewer can check the reasoning.
    """

    IDENTIFIER = "identifier"  # high-uniqueness coded string, e.g. CLM-88291
    DATE = "date"  # parses under a known date format
    CURRENCY = "currency"  # numeric, money-like magnitude/precision
    ENUM_CANDIDATE = "enum_candidate"  # low cardinality relative to sample count
    BOOLEAN = "boolean"
    NUMBER = "number"  # generic numeric, not money-like
    FREE_TEXT = "free_text"  # variable-length prose-like strings
    UNKNOWN = "unknown"


class NumericStats(BaseModel):
    """Aggregate statistics for numeric values."""

    model_config = _MODEL_CONFIG

    minimum: float
    maximum: float
    mean: float


class StringStats(BaseModel):
    """Aggregate statistics for string values."""

    model_config = _MODEL_CONFIG

    min_length: int
    max_length: int
    mean_length: float


class FieldProfile(BaseModel):
    """Statistical profile of one field across observed samples."""

    model_config = _MODEL_CONFIG

    json_path: str = Field(description="The field this profile describes.")
    sample_count: int = Field(description="Number of observed occurrences (incl. nulls).")
    present_count: int = Field(description="Occurrences where the field was present.")
    null_count: int = Field(description="Occurrences that were explicitly null.")
    null_rate: float = Field(description="null_count / sample_count (0 if no samples).")
    unique_count: int = Field(description="Distinct non-null values observed.")
    unique_rate: float = Field(
        description="unique_count / present_non_null_count (0 if none)."
    )
    observed_types: tuple[ObservedType, ...] = Field(
        description="Distinct runtime types seen (more than one => mixed)."
    )
    is_mixed_type: bool = Field(
        default=False, description="True if more than one non-null runtime type was seen."
    )
    numeric_stats: NumericStats | None = Field(default=None)
    string_stats: StringStats | None = Field(default=None)
    sample_values: tuple[str, ...] = Field(
        default=(),
        description="A capped set of example values (stringified) for inspection.",
    )
    detected_pattern: str | None = Field(
        default=None,
        description="A coarse structural signature of string values, e.g. "
        "'AAA-000' for a fixed alpha-dash-digit shape, when one dominates.",
    )
    detected_date_format: str | None = Field(
        default=None, description="strptime format that parsed the string values, if any."
    )
    semantic_type: SemanticType = Field(
        default=SemanticType.UNKNOWN,
        description="Heuristic meaning inferred from the stats above.",
    )
