from crosswalk_service import ServiceContext, create_mapping


def test_mapping_can_be_loaded_by_tenant() -> None:
    context = ServiceContext()
    record = create_mapping(context, "tenant-a", {"source": "id"})

    assert context.store.get("tenant-a", record.id) == record
