from crosswalk_cli import format_health
from crosswalk_contracts import HealthResponse


def test_cli_boundary_formats_shared_health_contract() -> None:
    assert format_health(HealthResponse(status="ok", version="integration")) == "ok integration"
