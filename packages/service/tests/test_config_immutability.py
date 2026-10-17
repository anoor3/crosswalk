import pytest
from crosswalk_service import ServiceConfig
from pydantic import ValidationError


def test_service_config_is_immutable() -> None:
    with pytest.raises(ValidationError):
        ServiceConfig().environment = "remote"
