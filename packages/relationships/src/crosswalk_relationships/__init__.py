"""Phase 7 relationship discovery primitives."""

from .errors import (
    DuplicateRelationshipError,
    InvalidRelationshipInputError,
    RelationshipError,
    UnsupportedRelationshipError,
)
from .models import (
    Cardinality,
    FieldReference,
    RelationshipAlternative,
    RelationshipCandidate,
    RelationshipEdge,
    RelationshipEvidence,
    RelationshipGraph,
    RelationshipNode,
    RelationshipStatus,
)
from .overlap import OverlapStats, overlap_stats
from .ranking import rank_relationships
from .scoring import score_relationship

__version__ = "0.1.0"

__all__ = [
    "Cardinality",
    "DuplicateRelationshipError",
    "FieldReference",
    "InvalidRelationshipInputError",
    "OverlapStats",
    "RelationshipAlternative",
    "RelationshipCandidate",
    "RelationshipEdge",
    "RelationshipError",
    "RelationshipEvidence",
    "RelationshipGraph",
    "RelationshipNode",
    "RelationshipStatus",
    "UnsupportedRelationshipError",
    "__version__",
    "overlap_stats",
    "rank_relationships",
    "score_relationship",
]
