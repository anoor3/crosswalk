from crosswalk_api.settings import ApiSettings


def test_production_environment() -> None:
    assert ApiSettings(environment="production").environment == "production"
