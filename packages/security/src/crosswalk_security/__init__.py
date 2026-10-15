"""Small security policies with explicit, testable behavior."""

from .ssrf import UnsafeUrlError, validate_outbound_url

__all__ = ["UnsafeUrlError", "validate_outbound_url"]
