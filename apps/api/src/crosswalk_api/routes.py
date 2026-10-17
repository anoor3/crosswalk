from crosswalk_contracts import HealthResponse
from fastapi import APIRouter

router = APIRouter()


@router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(status="ok", version="ready")
