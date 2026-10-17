from crosswalk_service import ServiceContext, create_mapping


def test_create_mapping_uses_context_store() -> None:
    record = create_mapping(ServiceContext(), "tenant-a", {"source": "id"})

    assert record.tenant_id == "tenant-a"
    assert record.mapping_json == {"source": "id"}
