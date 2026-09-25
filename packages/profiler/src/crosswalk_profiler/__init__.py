"""Crosswalk value profiling (Phase 3).

Computes deterministic per-field statistics from real sample payloads. No LLM
(PLANNER §16, CHECKER §15). Reusable independently of any AI system.

Public API::

    from crosswalk_profiler import profile_field, profile_fields, FieldProfile
"""

from __future__ import annotations

from .engine import profile_field, profile_fields, profile_values
from .extract import ExtractedValue, extract_values
from .profile import (
    FieldProfile,
    NumericStats,
    ObservedType,
    SemanticType,
    StringStats,
)

__version__ = "0.1.0"

__all__ = [
    "ExtractedValue",
    "FieldProfile",
    "NumericStats",
    "ObservedType",
    "SemanticType",
    "StringStats",
    "__version__",
    "extract_values",
    "profile_field",
    "profile_fields",
    "profile_values",
]
