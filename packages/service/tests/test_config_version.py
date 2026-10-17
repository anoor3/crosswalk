import pytest
from crosswalk_service import ServiceConfig
from pydantic import ValidationError


def test_service_config_rejects_blank_version() -> None:
    with pytest.raises(ValidationError):
        ServiceConfig(version="")
