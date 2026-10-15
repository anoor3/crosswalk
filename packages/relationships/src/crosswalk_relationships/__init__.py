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

__version__ = "0.1.0"

__all__ = [
    "Cardinality",
    "DuplicateRelationshipError",
    "FieldReference",
    "InvalidRelationshipInputError",
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
]
