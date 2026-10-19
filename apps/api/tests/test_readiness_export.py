from crosswalk_api import Readiness


def test_readiness_is_public() -> None:
    assert Readiness.__name__ == "Readiness"
