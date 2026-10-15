import pytest
from crosswalk_storage import ConflictError, VersionedStore


def test_store_enforces_tenant_and_optimistic_version() -> None:
    store = VersionedStore()
    record = store.create("tenant-a", {"status": "draft"})
    updated = store.update("tenant-a", record.id, 1, {"status": "approved"})
    assert updated.version == 2
    with pytest.raises(ConflictError):
        store.update("tenant-a", record.id, 1, {"status": "stale"})
    with pytest.raises(KeyError):
        store.get("tenant-b", record.id)
