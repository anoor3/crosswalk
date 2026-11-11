import pytest


def test_version_override(monkeypatch: pytest.MonkeyPatch) -> None:
    from crosswalk_api.settings import ApiSettings

    monkeypatch.setenv("CROSSWALK_VERSION", "1.2")
    assert ApiSettings.from_environment().version == "1.2"
