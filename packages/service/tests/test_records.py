import pytest
from crosswalk_service import ServiceContext, create_mapping, update_mapping
from crosswalk_storage import ConflictError


def test_create_mapping_uses_context_store() -> None:
    record = create_mapping(ServiceContext(), "tenant-a", {"source": "id"})

    assert record.tenant_id == "tenant-a"
    assert record.mapping_json == {"source": "id"}


def test_update_mapping_increments_version() -> None:
    context = ServiceContext()
    record = create_mapping(context, "tenant-a", {"source": "id"})

    updated = update_mapping(
        context, "tenant-a", record.id, record.version, {"source": "external_id"}
    )

    assert updated.version == 2
    assert updated.mapping_json == {"source": "external_id"}


def test_update_mapping_rejects_stale_version() -> None:
    context = ServiceContext()
    record = create_mapping(context, "tenant-a", {"source": "id"})
    update_mapping(context, "tenant-a", record.id, 1, {"source": "external_id"})

    with pytest.raises(ConflictError):
        update_mapping(context, "tenant-a", record.id, 1, {"source": "name"})
