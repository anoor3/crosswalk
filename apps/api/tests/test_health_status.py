import pytest
from crosswalk_contracts import HealthResponse
from pydantic import ValidationError


def test_health_contract_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        HealthResponse(status="unknown", version="1")
