from datetime import UTC, datetime

from crosswalk_contracts import CreateJobRequest, HealthResponse, JobResponse, JobStatusResponse
from crosswalk_service import ServiceContext, submit_job
from fastapi import APIRouter, Request

router = APIRouter()


def _context(request: Request) -> ServiceContext:
    return request.app.state.service_context


@router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(status="ok", version="ready")


@router.get("/version", response_model=HealthResponse)
def version() -> HealthResponse:
    return HealthResponse(status="ok", version="service")


@router.get("/jobs/{job_id}", response_model=JobResponse)
def job_status(request: Request, job_id: str) -> JobResponse:
    job = _context(request).jobs.get(job_id)
    return JobResponse(
        id=job_id,
        status=job.status.value.lower() if job else "queued",
        progress=job.progress if job else 0,
    )


@router.get("/jobs/{job_id}/state", response_model=JobStatusResponse)
def job_state(request: Request, job_id: str) -> JobStatusResponse:
    job = _context(request).jobs.get(job_id)
    return JobStatusResponse(id=job_id, status=job.status.value if job else "QUEUED")


@router.post("/jobs", response_model=JobResponse, status_code=201)
def create_job(request: CreateJobRequest, http_request: Request) -> JobResponse:
    job = submit_job(_context(http_request), request.tenant_id, request.kind, datetime.now(UTC))
    return JobResponse(id=job.id, status=job.status.value.lower(), progress=job.progress)
