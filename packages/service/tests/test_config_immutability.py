import pytest
from crosswalk_service import ServiceConfig
from pydantic import ValidationError


def test_service_config_is_immutable() -> None:
    with pytest.raises(ValidationError):
        ServiceConfig.model_validate(
            {"name": "api", "version": "1", "environment": "local", "region": "us"}
        )
