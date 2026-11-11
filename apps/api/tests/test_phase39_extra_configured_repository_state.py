from pathlib import Path

from crosswalk_api import create_app
from crosswalk_api.settings import ApiSettings


def candidate() -> dict[str, object]:
    return {
        "external_path": "$.id",
        "canonical_path": None,
        "score": 0,
        "status": "UNRESOLVED",
        "evidence": None,
    }


def test_configured_repository_state(tmp_path: Path) -> None:
    app = create_app(settings=ApiSettings(review_database=str(tmp_path / "r.db")))
    assert app.state.review_repository is not None
