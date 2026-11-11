from crosswalk_api.settings import ApiSettings


def test_database_optional() -> None:
    assert ApiSettings().review_database is None
