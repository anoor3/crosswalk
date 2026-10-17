from crosswalk_contracts import ServiceInfoResponse


def test_service_info_contract_serializes() -> None:
    value = ServiceInfoResponse(name="api", version="1", environment="local")

    assert value.model_dump() == {
        "name": "api",
        "version": "1",
        "environment": "local",
    }
