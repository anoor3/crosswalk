from crosswalk_api import Readiness


def test_ready_state_defaults_to_ok() -> None:
    assert Readiness().status == "ok"
