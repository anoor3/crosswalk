"""Crosswalk's deterministic baseline mapper (PLANNER §17, CHECKER §§7-11)."""

from .engine import map_fields
from .models import (
    CanonicalField,
    MappingAlternative,
    MappingCandidate,
    MappingEvidence,
    MappingStatus,
    SignalEvidence,
)
from .targets import canonical_fields

__version__ = "0.1.0"

__all__ = [
    "CanonicalField",
    "MappingAlternative",
    "MappingCandidate",
    "MappingEvidence",
    "MappingStatus",
    "SignalEvidence",
    "__version__",
    "canonical_fields",
    "map_fields",
]
