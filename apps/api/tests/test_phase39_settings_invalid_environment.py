import pytest
from crosswalk_api.settings import ApiSettings
from pydantic import ValidationError


def test_invalid_environment() -> None:
    with pytest.raises(ValidationError):
        ApiSettings(environment="invalid")
