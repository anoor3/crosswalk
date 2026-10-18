from crosswalk_api.settings import ApiSettings


def test_api_settings_defaults_to_local_docs() -> None:
    settings = ApiSettings()

    assert settings.environment == "local"
    assert settings.enable_docs
