from crosswalk_api import Readiness


def test_ready_state_can_be_degraded() -> None:
    assert Readiness(ready=False).status == "degraded"
