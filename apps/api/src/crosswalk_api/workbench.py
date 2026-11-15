"""Local workbench discovery boundary; inputs never trigger outbound requests."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from crosswalk_discovery import DiscoveryError, analyze_openapi
from crosswalk_mapping import canonical_fields, map_fields
from crosswalk_profiler import profile_fields

from .remote_import import RemoteImportError, fetch_openapi

router = APIRouter(prefix="/workbench")


class AnalyzeRequest(BaseModel):
    spec: dict[str, object]
    samples: list[dict[str, object]] = Field(default_factory=list, max_length=200)
    method: str = "GET"
    path: str | None = None


class RemoteImportRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


@router.post("/remote-openapi")
def remote_openapi(request: RemoteImportRequest) -> dict[str, object]:
    try:
        document = fetch_openapi(request.url)
    except RemoteImportError as error:
        raise HTTPException(422, str(error)) from error
    return {
        "url": document.url,
        "bytes": document.bytes_read,
        "content_type": document.content_type,
        "spec": document.document,
    }


@router.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, object]:
    try:
        catalog = analyze_openapi(request.spec)
        endpoints = [e for e in catalog.endpoints if e.response_fields]
        endpoint = (
            next(
                (e for e in endpoints if e.path == request.path and e.method == request.method),
                None,
            )
            if request.path
            else next(iter(endpoints), None)
        )
        if endpoint is None:
            raise HTTPException(422, "Select an endpoint with a response schema.")
        profiles = profile_fields(request.samples, (f.json_path for f in endpoint.response_fields))
        candidates = map_fields(endpoint.response_fields, profiles)
        return {
            "catalog": catalog.model_dump(mode="json"),
            "endpoint": endpoint.model_dump(mode="json"),
            "candidates": [c.model_dump(mode="json") for c in candidates],
            "profiles": [p.model_dump(mode="json") for p in profiles.values()],
            "targets": [t.path for t in canonical_fields()],
        }
    except (DiscoveryError, ValueError, RecursionError) as error:
        raise HTTPException(
            422, "Could not analyze this document. Check its OpenAPI response schemas."
        ) from error


@router.get("/example")
def example() -> dict[str, object]:
    import json

    root = Path(__file__).resolve().parents[4]
    return {
        "spec": json.loads((root / "fixtures/schemas/easy/openapi.json").read_text()),
        "samples": json.loads((root / "fixtures/payloads/easy/claims.json").read_text()),
        "path": "/claims/{claim_number}",
    }
