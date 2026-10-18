import pytest
from crosswalk_api.settings import ApiSettings
from pydantic import ValidationError


def test_api_settings_rejects_unknown_environment() -> None:
    with pytest.raises(ValidationError):
        ApiSettings(environment="sandbox")
