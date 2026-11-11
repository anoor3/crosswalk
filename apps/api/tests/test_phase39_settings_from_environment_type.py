from crosswalk_api.settings import ApiSettings


def test_from_environment_type() -> None:
    assert isinstance(ApiSettings.from_environment(), ApiSettings)
