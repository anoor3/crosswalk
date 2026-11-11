from crosswalk_api import create_app


def candidate() -> dict[str, object]:
    return {
        "external_path": "$.id",
        "canonical_path": None,
        "score": 0,
        "status": "UNRESOLVED",
        "evidence": None,
    }


def test_memory_repository_state() -> None:
    assert create_app().state.review_repository is None
