from crosswalk_contracts import ErrorEnvelope
from fastapi import Request
from fastapi.responses import JSONResponse

from .trace import TRACE_HEADER


class ApiInputError(ValueError):
    pass


def input_error_handler(request: Request, error: Exception) -> JSONResponse:
    payload = ErrorEnvelope(
        code="invalid_input",
        message=str(error),
        trace_id=request.headers.get(TRACE_HEADER, "local"),
    )
    return JSONResponse(status_code=400, content=payload.model_dump(mode="json"))
