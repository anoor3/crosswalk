from crosswalk_cli import format_health
from crosswalk_contracts import HealthResponse


def test_health_format_is_human_readable() -> None:
    assert format_health(HealthResponse(status="ok", version="1.2")) == "ok 1.2"
