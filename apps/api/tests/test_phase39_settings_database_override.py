import pytest


def test_database_override(monkeypatch: pytest.MonkeyPatch) -> None:
    from crosswalk_api.settings import ApiSettings

    monkeypatch.setenv("CROSSWALK_REVIEW_DATABASE", "reviews.db")
    assert ApiSettings.from_environment().review_database == "reviews.db"
