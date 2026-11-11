from crosswalk_api.settings import ApiSettings


def test_version_read() -> None:
    assert ApiSettings(version="v").version == "v"
