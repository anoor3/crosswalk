import pytest
from crosswalk_api.settings import ApiSettings
from pydantic import ValidationError


def test_version_required() -> None:
    with pytest.raises(ValidationError):
        ApiSettings(version="")
