from .config import DeploymentConfig, Environment


def readiness_checks(config: DeploymentConfig) -> tuple[str, ...]:
    checks = ["image configured", "health path configured"]
    if config.environment in (Environment.STAGING, Environment.PRODUCTION):
        checks.extend(("https required", "migrations required"))
    return tuple(checks)
