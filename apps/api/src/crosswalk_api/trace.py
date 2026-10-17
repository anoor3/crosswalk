from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response

TRACE_HEADER = "X-Trace-Id"


def trace_id(request: Request) -> str:
    """Return the caller trace id or create one for a local request."""

    return request.headers.get(TRACE_HEADER, uuid4().hex)


async def add_trace_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Attach a stable trace identifier to every API response."""

    response = await call_next(request)
    response.headers[TRACE_HEADER] = trace_id(request)
    return response
