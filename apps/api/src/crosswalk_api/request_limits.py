from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

MAX_REQUEST_BYTES = 1_048_576


async def enforce_request_limit(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Reject oversized requests before application parsing."""

    length = request.headers.get("content-length")
    try:
        size = int(length) if length is not None else 0
    except ValueError:
        size = MAX_REQUEST_BYTES + 1
    if size > MAX_REQUEST_BYTES:
        return JSONResponse(status_code=413, content={"detail": "request too large"})
    return await call_next(request)
