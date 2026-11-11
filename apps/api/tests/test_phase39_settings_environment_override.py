import pytest


def test_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    from crosswalk_api.settings import ApiSettings

    monkeypatch.setenv("CROSSWALK_ENVIRONMENT", "staging")
    assert ApiSettings.from_environment().environment == "staging"
