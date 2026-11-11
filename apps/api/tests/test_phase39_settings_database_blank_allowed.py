from crosswalk_api.settings import ApiSettings


def test_database_blank_allowed() -> None:
    assert ApiSettings(review_database="").review_database == ""
