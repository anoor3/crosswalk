"""Typed failures for review workflow callers."""

from __future__ import annotations


class ReviewError(ValueError):
    """Base class for review-domain errors."""


class DuplicateReviewError(ReviewError):
    """A review ID already exists."""


class ReviewNotFoundError(ReviewError):
    """The requested review does not exist."""


class StaleReviewError(ReviewError):
    """The caller attempted to update an old review version."""


class InvalidReviewActionError(ReviewError):
    """The action is not valid for the current review state or candidate."""
