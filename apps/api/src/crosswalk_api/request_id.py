from uuid import uuid4


def request_trace_id(header: str | None) -> str:
    value = (header or "").strip()
    return value[:128] if value else uuid4().hex
