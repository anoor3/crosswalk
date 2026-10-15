"""Small deterministic safeguards for investigation audit records."""

from __future__ import annotations

import re

_SENSITIVE = re.compile(
    r"(?i)(api[_-]?key|authorization|password|secret|token)\s*[:=]\s*(?:Bearer\s+)?[^,;\s]+"
)


def redact_summary(value: str, limit: int = 1000) -> str:
    """Remove common credential-shaped values before storing an audit summary."""
    return _SENSITIVE.sub(lambda match: f"{match.group(1)}=[REDACTED]", value)[:limit]
