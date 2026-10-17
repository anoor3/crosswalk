import pytest
from crosswalk_contracts import ServiceInfoResponse
from pydantic import ValidationError


def test_service_info_requires_version() -> None:
    with pytest.raises(ValidationError):
        ServiceInfoResponse(name="api", version="", environment="local")
