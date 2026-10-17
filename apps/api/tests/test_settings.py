import pytest
from crosswalk_api import ApiSettings


def test_settings_restrict_environment_names() -> None:
    assert ApiSettings(environment="staging").environment == "staging"
    with pytest.raises(ValueError):
        ApiSettings(environment="unknown")
