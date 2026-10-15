"""Typed failures for relationship discovery."""

from __future__ import annotations


class RelationshipError(ValueError):
    """Base relationship-domain error."""


class InvalidRelationshipInputError(RelationshipError):
    """Input fields or samples cannot be compared safely."""


class DuplicateRelationshipError(RelationshipError):
    """The same source/target relationship was supplied more than once."""


class UnsupportedRelationshipError(RelationshipError):
    """The requested relationship shape is not supported by this baseline."""
