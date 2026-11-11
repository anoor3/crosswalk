from pathlib import Path

from crosswalk_api.settings import ApiSettings


def candidate() -> dict[str, object]:
    return {
        "external_path": "$.id",
        "canonical_path": None,
        "score": 0,
        "status": "UNRESOLVED",
        "evidence": None,
    }


def test_settings_db_path(tmp_path: Path) -> None:
    assert ApiSettings(review_database=str(tmp_path / "r.db")).review_database is not None
