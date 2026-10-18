from __future__ import annotations

from crosswalk_contracts import HealthResponse, ServiceInfoResponse
from crosswalk_service import ServiceConfig
from fastapi import FastAPI

from .errors import ApiInputError, input_error_handler
from .request_limits import enforce_request_limit
from .routes import router
from .security_headers import add_security_headers
from .trace import add_trace_header


def create_app(version: str = "development", environment: str = "local") -> FastAPI:
    config = ServiceConfig(version=version, environment=environment)
    app = FastAPI(title="Crosswalk API", version=config.version)
    app.middleware("http")(add_trace_header)
    app.middleware("http")(enforce_request_limit)
    app.middleware("http")(add_security_headers)
    app.add_exception_handler(ApiInputError, input_error_handler)
    app.include_router(router)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", version=config.version)

    @app.get("/info", response_model=ServiceInfoResponse)
    def info() -> ServiceInfoResponse:
        return ServiceInfoResponse(
            name=config.name, version=config.version, environment=config.environment
        )

    return app
