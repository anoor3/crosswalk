"""Typed failures for enum mapping and runtime translation."""

from __future__ import annotations


class EnumMappingError(ValueError):
    """Base error for enum mapping."""


class InvalidEnumVocabularyError(EnumMappingError):
    """Declared or explicit enum values are inconsistent."""


class UnknownEnumValueError(EnumMappingError):
    """A runtime value was not observed or declared."""


class UnapprovedEnumMappingError(EnumMappingError):
    """A known value has only a review-required or conflicting hypothesis."""
