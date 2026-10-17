import pytest
from crosswalk_contracts import ServiceInfoResponse
from pydantic import ValidationError


def test_service_info_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ServiceInfoResponse(name="api", version="1", environment="local", region="us")
