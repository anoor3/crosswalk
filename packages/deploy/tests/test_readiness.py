from crosswalk_deploy import DeploymentConfig, Environment, readiness_checks


def test_staging_readiness_includes_operational_checks() -> None:
    config = DeploymentConfig(environment=Environment.STAGING, service_name="api", image="x")
    assert "https required" in readiness_checks(config)
