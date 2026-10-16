from crosswalk_storage import VersionedStore


def test_storage_boundary_keeps_records_tenant_scoped() -> None:
    store = VersionedStore()
    record = store.create("tenant", {"status": "draft"})
    assert store.get("tenant", record.id).mapping_json["status"] == "draft"
