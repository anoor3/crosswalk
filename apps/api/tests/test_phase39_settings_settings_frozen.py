import pytest
from crosswalk_api.settings import ApiSettings


def test_settings_frozen() -> None:
    with pytest.raises(Exception):  # noqa: B017
        ApiSettings().version = "x"  # type: ignore[misc]
