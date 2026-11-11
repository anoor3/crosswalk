import pytest


def test_default_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    from crosswalk_api.settings import ApiSettings

    monkeypatch.delenv("CROSSWALK_ENVIRONMENT", raising=False)
    assert ApiSettings.from_environment().environment == "local"
