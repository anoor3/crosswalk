import pytest
from crosswalk_api.settings import ApiSettings
from pydantic import ValidationError


def test_settings_extra_forbidden() -> None:
    with pytest.raises(ValidationError):
        ApiSettings(extra="x")  # type: ignore[call-arg]
