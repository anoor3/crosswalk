from crosswalk_service import ServiceConfig


def test_service_config_has_local_defaults() -> None:
    config = ServiceConfig()

    assert config.name == "crosswalk-api"
    assert config.environment == "local"
