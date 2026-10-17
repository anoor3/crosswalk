from crosswalk_contracts import ErrorEnvelope
from fastapi import Request
from fastapi.responses import JSONResponse


class ApiInputError(ValueError):
    pass


def input_error_handler(_: Request, error: Exception) -> JSONResponse:
    payload = ErrorEnvelope(code="invalid_input", message=str(error), trace_id="local")
    return JSONResponse(status_code=400, content=payload.model_dump(mode="json"))
