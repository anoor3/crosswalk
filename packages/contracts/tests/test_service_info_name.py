import pytest
from crosswalk_contracts import ServiceInfoResponse
from pydantic import ValidationError


def test_service_info_requires_name() -> None:
    with pytest.raises(ValidationError):
        ServiceInfoResponse(name="", version="1", environment="local")
