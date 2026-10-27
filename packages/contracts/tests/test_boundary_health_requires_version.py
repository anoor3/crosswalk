import pytest
from crosswalk_contracts import HealthResponse
from pydantic import ValidationError


def test_health_requires_version() -> None:
    with pytest.raises(ValidationError):
        HealthResponse(status="ok", version="")
