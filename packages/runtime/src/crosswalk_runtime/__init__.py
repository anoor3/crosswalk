"""Failure-aware runtime primitives without embedded credentials or I/O."""

from .errors import AuthenticationError, CanonicalValidationError, ExternalTimeout, RateLimitError
from .policies import RetryPolicy, retry_delay

__all__ = [
    "AuthenticationError",
    "CanonicalValidationError",
    "ExternalTimeout",
    "RateLimitError",
    "RetryPolicy",
    "retry_delay",
]
