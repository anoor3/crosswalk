from crosswalk_api.settings import ApiSettings


def test_environment_read() -> None:
    assert ApiSettings(environment="local").environment == "local"
