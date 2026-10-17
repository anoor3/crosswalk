from __future__ import annotations

from crosswalk_contracts import HealthResponse, ServiceInfoResponse
from fastapi import FastAPI

from .errors import ApiInputError, input_error_handler
from .routes import router
from .trace import add_trace_header


def create_app(version: str = "development") -> FastAPI:
    app = FastAPI(title="Crosswalk API", version=version)
    app.middleware("http")(add_trace_header)
    app.add_exception_handler(ApiInputError, input_error_handler)
    app.include_router(router)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", version=version)

    @app.get("/info", response_model=ServiceInfoResponse)
    def info() -> ServiceInfoResponse:
        return ServiceInfoResponse(name="crosswalk-api", version=version, environment="local")

    return app
