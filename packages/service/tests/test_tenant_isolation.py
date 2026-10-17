import pytest
from crosswalk_service import ServiceContext, create_mapping


def test_mapping_isolation_rejects_other_tenant() -> None:
    context = ServiceContext()
    record = create_mapping(context, "tenant-a", {"source": "id"})

    with pytest.raises(KeyError):
        context.store.get("tenant-b", record.id)
