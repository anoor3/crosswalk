import re

_SECRET = re.compile(r"(?i)(token|password|secret|api[_-]?key)\s*=\s*[^\s,;]+")


def redact_audit_text(value: str) -> str:
    return _SECRET.sub(lambda match: f"{match.group(1)}=[REDACTED]", value)[:1000]
