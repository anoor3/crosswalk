import pytest
from crosswalk_deploy import DeploymentConfig, Environment


def test_production_config_requires_explicit_https_defaults() -> None:
    config = DeploymentConfig(
        environment=Environment.PRODUCTION, service_name="crosswalk-api", image="crosswalk:latest"
    )
    assert config.https_required is True
    assert config.migrations_required is True


def test_service_names_are_safe() -> None:
    with pytest.raises(ValueError):
        DeploymentConfig(environment=Environment.LOCAL, service_name="Bad Name", image="x")
