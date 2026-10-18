from crosswalk_contracts import HealthResponse


def test_health_contract_serializes() -> None:
    assert HealthResponse(status="ok", version="1").model_dump() == {
        "status": "ok",
        "version": "1",
    }
