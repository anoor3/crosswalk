from crosswalk_storage import MappingRecord

from .context import ServiceContext


def create_mapping(
    context: ServiceContext, tenant_id: str, mapping_json: dict[str, object]
) -> MappingRecord:
    """Persist a tenant-owned mapping through the configured storage seam."""

    return context.store.create(tenant_id, mapping_json)


def update_mapping(
    context: ServiceContext,
    tenant_id: str,
    record_id: str,
    expected_version: int,
    mapping_json: dict[str, object],
) -> MappingRecord:
    """Update a mapping while preserving optimistic version checks."""

    return context.store.update(
        tenant_id, record_id, expected_version, mapping_json
    )
