from crosswalk_api.settings import ApiSettings


def candidate() -> dict[str, object]:
    return {
        "external_path": "$.id",
        "canonical_path": None,
        "score": 0,
        "status": "UNRESOLVED",
        "evidence": None,
    }


def test_settings_environment_factory() -> None:
    assert ApiSettings.from_environment().version
