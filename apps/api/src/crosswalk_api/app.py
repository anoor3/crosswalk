from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from crosswalk_contracts import EventResponse, HealthResponse, ServiceInfoResponse
from crosswalk_service import ServiceConfig, ServiceContext
from crosswalk_storage import SQLiteReviewRepository
from fastapi import FastAPI, Request, Response

from .errors import ApiInputError, input_error_handler
from .logging import EventLog
from .metrics import Metrics
from .request_limits import enforce_request_limit
from .routes import router
from .security_headers import add_security_headers
from .settings import ApiSettings
from .trace import add_trace_header


def create_app(
    version: str = "development",
    environment: str = "local",
    metrics: Metrics | None = None,
    events: EventLog | None = None,
    context: ServiceContext | None = None,
    settings: ApiSettings | None = None,
) -> FastAPI:
    api_settings = settings or ApiSettings(version=version, environment=environment)
    config = ServiceConfig(version=api_settings.version, environment=api_settings.environment)
    registry = metrics or Metrics()
    event_log = events or EventLog()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        if repository is not None:
            repository.close()

    app = FastAPI(title="Crosswalk API", version=config.version, lifespan=lifespan)
    repository = (
        SQLiteReviewRepository(api_settings.review_database)
        if context is None and api_settings.review_database
        else None
    )
    app.state.review_repository = repository
    app.state.service_context = context or ServiceContext(review_repository=repository)
    app.middleware("http")(add_trace_header)
    app.middleware("http")(enforce_request_limit)

    @app.middleware("http")
    async def count_requests(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        registry.increment("requests.total")
        event_log.record("request.received", {"path": request.url.path})
        return await call_next(request)

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

    @app.get("/metrics")
    def metrics_endpoint() -> dict[str, int]:
        return registry.snapshot()

    @app.get("/events", response_model=tuple[EventResponse, ...])
    def events_endpoint() -> tuple[dict[str, str], ...]:
        return event_log.snapshot()

    return app
