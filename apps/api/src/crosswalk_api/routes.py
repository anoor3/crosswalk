from crosswalk_contracts import HealthResponse, JobResponse
from fastapi import APIRouter

router = APIRouter()


@router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(status="ok", version="ready")


@router.get("/version", response_model=HealthResponse)
def version() -> HealthResponse:
    return HealthResponse(status="ok", version="service")


@router.get("/jobs/{job_id}", response_model=JobResponse)
def job_status(job_id: str) -> JobResponse:
    return JobResponse(id=job_id, status="queued", progress=0)
