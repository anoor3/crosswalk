from crosswalk_service import ServiceContext, create_mapping


def test_mapping_create_copies_input() -> None:
    context = ServiceContext()
    payload: dict[str, object] = {"source": "id"}
    record = create_mapping(context, "tenant-a", payload)
    payload["source"] = "changed"

    assert record.mapping_json == {"source": "id"}
