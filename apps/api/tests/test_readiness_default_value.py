from crosswalk_api import Readiness


def test_readiness_defaults_ready() -> None:
    assert Readiness().ready is True
