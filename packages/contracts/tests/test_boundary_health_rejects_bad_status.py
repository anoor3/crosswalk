import pytest
from crosswalk_contracts import HealthResponse
from pydantic import ValidationError


def test_health_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        HealthResponse(status="bad", version="v")
