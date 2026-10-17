from crosswalk_service import ServiceContext


def test_context_owns_explicit_local_dependencies() -> None:
    context = ServiceContext()
    record = context.store.create("tenant", {"status": "draft"})
    assert context.store.get("tenant", record.id).mapping_json["status"] == "draft"
    assert len(context.queue) == 0
