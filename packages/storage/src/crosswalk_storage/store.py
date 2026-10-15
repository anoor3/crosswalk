from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class ConflictError(RuntimeError):
    """Raised when a stale version attempts to overwrite a record."""


class MappingRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    mapping_json: dict[str, object]
    version: int = Field(default=1, ge=1)


class VersionedStore:
    """A small persistence seam mirroring transactional optimistic locking."""

    def __init__(self) -> None:
        self._records: dict[str, MappingRecord] = {}

    def create(self, tenant_id: str, mapping_json: dict[str, object]) -> MappingRecord:
        record = MappingRecord(
            id=str(uuid4()), tenant_id=tenant_id, mapping_json=dict(mapping_json)
        )
        self._records[record.id] = record
        return record

    def get(self, tenant_id: str, record_id: str) -> MappingRecord:
        record = self._records[record_id]
        if record.tenant_id != tenant_id:
            raise KeyError(record_id)
        return record

    def update(
        self, tenant_id: str, record_id: str, expected_version: int, mapping_json: dict[str, object]
    ) -> MappingRecord:
        current = self.get(tenant_id, record_id)
        if current.version != expected_version:
            raise ConflictError("stale mapping version")
        self._records[record_id] = current.model_copy(
            update={"mapping_json": dict(mapping_json), "version": current.version + 1}
        )
        return self._records[record_id]
