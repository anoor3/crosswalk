from crosswalk_api.settings import ApiSettings


def test_database_path_read() -> None:
    assert ApiSettings(review_database="reviews.db").review_database is not None
