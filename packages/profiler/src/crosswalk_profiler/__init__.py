"""Crosswalk value profiling (Phase 3).

Computes deterministic per-field statistics from real sample payloads. No LLM
(PLANNER §16, CHECKER §15). Reusable independently of any AI system.

Public API (grows over Phase 3)::

    from crosswalk_profiler import FieldProfile, SemanticType
"""

from __future__ import annotations

from .profile import (
    FieldProfile,
    NumericStats,
    ObservedType,
    SemanticType,
    StringStats,
)

__version__ = "0.1.0"

__all__ = [
    "FieldProfile",
    "NumericStats",
    "ObservedType",
    "SemanticType",
    "StringStats",
    "__version__",
]
