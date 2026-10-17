from crosswalk_service import ServiceConfig


def test_service_config_accepts_custom_values() -> None:
    config = ServiceConfig(name="worker", version="3", environment="test")

    assert (config.name, config.version, config.environment) == ("worker", "3", "test")
