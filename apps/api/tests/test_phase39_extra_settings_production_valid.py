from crosswalk_api.settings import ApiSettings


def candidate() -> dict[str, object]:
    return {
        "external_path": "$.id",
        "canonical_path": None,
        "score": 0,
        "status": "UNRESOLVED",
        "evidence": None,
    }


def test_settings_production_valid() -> None:
    assert ApiSettings(environment="production").environment == "production"
