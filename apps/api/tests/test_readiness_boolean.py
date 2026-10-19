from crosswalk_api import Readiness


def test_readiness_status_uses_boolean() -> None:
    assert Readiness(ready=True).status == "ok"
    assert Readiness(ready=False).status == "degraded"
