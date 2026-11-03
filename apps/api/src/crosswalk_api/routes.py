from datetime import UTC, datetime
from typing import cast

from crosswalk_contracts import (
    CancelJobRequest,
    CreateJobRequest,
    CreateMappingRequest,
    EvaluationExampleResponse,
    HealthResponse,
    JobResponse,
    JobStatusResponse,
    MappingResponse,
    OpenReviewRequest,
    Page,
    ReviewDecisionRequest,
    ReviewResponse,
    UpdateMappingRequest,
)
from crosswalk_review import (
    ReviewActionType,
    ReviewNotFoundError,
    ReviewRecord,
    ReviewState,
    StaleReviewError,
)
from crosswalk_service import (
    ServiceContext,
    cancel_job,
    create_mapping,
    delete_mapping,
    list_mappings,
    submit_job,
    update_mapping,
)
from crosswalk_storage import ConflictError
from fastapi import APIRouter, HTTPException, Query, Request

from crosswalk_mapping import MappingCandidate

router = APIRouter()


def _review_response(record: ReviewRecord) -> ReviewResponse:
    return ReviewResponse(
        review_id=record.review_id,
        external_path=record.external_path,
        state=record.state.value,
        canonical_path=record.canonical_path,
        version=record.version,
    )


def _context(request: Request) -> ServiceContext:
    return cast(ServiceContext, request.app.state.service_context)


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


@router.get("/jobs", response_model=Page[JobResponse])
def list_jobs(
    request: Request, tenant_id: str, limit: int = Query(default=100, ge=1, le=1000)
) -> Page[JobResponse]:
    jobs = _context(request).jobs.snapshot_for_tenant(tenant_id)[:limit]
    return Page(
        items=tuple(
            JobResponse(id=job.id, status=job.status.value.lower(), progress=job.progress)
            for job in jobs
        )
    )


@router.get("/jobs/{job_id}/state", response_model=JobStatusResponse)
def job_state(request: Request, job_id: str) -> JobStatusResponse:
    job = _context(request).jobs.get(job_id)
    return JobStatusResponse(id=job_id, status=job.status.value if job else "QUEUED")


@router.post("/jobs", response_model=JobResponse, status_code=201)
def create_job(request: CreateJobRequest, http_request: Request) -> JobResponse:
    job = submit_job(_context(http_request), request.tenant_id, request.kind, datetime.now(UTC))
    return JobResponse(id=job.id, status=job.status.value.lower(), progress=job.progress)


@router.post("/jobs/{job_id}/cancel", response_model=JobResponse)
def cancel_job_route(job_id: str, request: CancelJobRequest, http_request: Request) -> JobResponse:
    job = cancel_job(_context(http_request), request.tenant_id, job_id, datetime.now(UTC))
    if job is None:
        current = _context(http_request).jobs.get_for_tenant(request.tenant_id, job_id)
        return JobResponse(
            id=job_id,
            status=current.status.value.lower() if current else "queued",
            progress=current.progress if current else 0,
        )
    return JobResponse(id=job.id, status=job.status.value.lower(), progress=job.progress)


@router.post("/mappings", response_model=MappingResponse, status_code=201)
def create_mapping_route(request: CreateMappingRequest, http_request: Request) -> MappingResponse:
    record = create_mapping(_context(http_request), request.tenant_id, request.mapping)
    return MappingResponse(
        id=record.id,
        tenant_id=record.tenant_id,
        mapping=record.mapping_json,
        version=record.version,
    )


@router.get("/mappings", response_model=Page[MappingResponse])
def list_mapping_route(tenant_id: str, http_request: Request) -> Page[MappingResponse]:
    records = list_mappings(_context(http_request), tenant_id)
    return Page(
        items=tuple(
            MappingResponse(
                id=record.id,
                tenant_id=record.tenant_id,
                mapping=record.mapping_json,
                version=record.version,
            )
            for record in records
        )
    )


@router.get("/mappings/{record_id}", response_model=MappingResponse)
def get_mapping_route(record_id: str, tenant_id: str, http_request: Request) -> MappingResponse:
    try:
        record = _context(http_request).store.get(tenant_id, record_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="mapping not found") from error
    return MappingResponse(
        id=record.id,
        tenant_id=record.tenant_id,
        mapping=record.mapping_json,
        version=record.version,
    )


@router.put("/mappings/{record_id}", response_model=MappingResponse)
def update_mapping_route(
    record_id: str, request: UpdateMappingRequest, http_request: Request
) -> MappingResponse:
    try:
        record = update_mapping(
            _context(http_request),
            request.tenant_id,
            record_id,
            request.expected_version,
            request.mapping,
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail="mapping not found") from error
    except ConflictError as error:
        raise HTTPException(status_code=409, detail="stale mapping version") from error
    return MappingResponse(
        id=record.id,
        tenant_id=record.tenant_id,
        mapping=record.mapping_json,
        version=record.version,
    )


@router.delete("/mappings/{record_id}", status_code=204)
def delete_mapping_route(record_id: str, tenant_id: str, http_request: Request) -> None:
    try:
        delete_mapping(_context(http_request), tenant_id, record_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="mapping not found") from error


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
def open_review_route(request: OpenReviewRequest, http_request: Request) -> ReviewResponse:
    try:
        record = _context(http_request).reviews.open(
            request.tenant_id,
            request.review_id,
            MappingCandidate.model_validate(request.candidate),
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return _review_response(record)


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
def get_review_route(review_id: str, tenant_id: str, http_request: Request) -> ReviewResponse:
    try:
        record = _context(http_request).reviews.get(tenant_id, review_id)
    except ReviewNotFoundError as error:
        raise HTTPException(status_code=404, detail="review not found") from error
    return _review_response(record)


@router.get("/reviews", response_model=Page[ReviewResponse])
def list_reviews_route(
    tenant_id: str, http_request: Request, state: ReviewState | None = None
) -> Page[ReviewResponse]:
    records = _context(http_request).reviews.list_all(tenant_id)
    if state is not None:
        records = tuple(record for record in records if record.state is state)
    return Page(items=tuple(_review_response(record) for record in records))


@router.post("/reviews/{review_id}/decision", response_model=ReviewResponse)
def decide_review_route(
    review_id: str, request: ReviewDecisionRequest, http_request: Request
) -> ReviewResponse:
    try:
        action = ReviewActionType(request.action)
        record = _context(http_request).reviews.decide(
            request.tenant_id,
            review_id,
            action=action,
            reviewer_id=request.reviewer_id,
            expected_version=request.expected_version,
            rationale=request.rationale,
            canonical_path=request.canonical_path,
        )
    except StaleReviewError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except (ReviewNotFoundError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return _review_response(record)


@router.get("/reviews/{review_id}/example", response_model=EvaluationExampleResponse)
def review_example_route(
    review_id: str, tenant_id: str, http_request: Request
) -> EvaluationExampleResponse:
    try:
        example = _context(http_request).reviews.evaluation_example(tenant_id, review_id)
    except ReviewNotFoundError as error:
        raise HTTPException(status_code=404, detail="review not found") from error
    if example is None:
        raise HTTPException(status_code=409, detail="review has no evaluation example")
    return EvaluationExampleResponse.model_validate(example.model_dump())
