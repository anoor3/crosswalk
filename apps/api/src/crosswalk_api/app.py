from __future__ import annotations

from crosswalk_contracts import HealthResponse
from fastapi import FastAPI


def create_app(version: str = "development") -> FastAPI:
    app = FastAPI(title="Crosswalk API", version=version)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", version=version)

    return app
