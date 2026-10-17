from crosswalk_contracts import CreateJobRequest, HealthResponse, JobResponse
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


@router.post("/jobs", response_model=JobResponse, status_code=201)
def create_job(request: CreateJobRequest) -> JobResponse:
    return JobResponse(id=f"local-{request.kind}", status="queued", progress=0)
