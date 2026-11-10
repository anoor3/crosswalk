"""Persistence contracts for tenant-scoped review records."""

from __future__ import annotations

from typing import Protocol

from .models import ReviewRecord


class ReviewRepository(Protocol):
    """Minimal repository contract a database adapter can implement later."""

    def get(self, tenant_id: str, review_id: str) -> ReviewRecord: ...

    def list(self, tenant_id: str) -> tuple[ReviewRecord, ...]: ...

    def save(
        self, tenant_id: str, record: ReviewRecord, *, expected_version: int | None
    ) -> ReviewRecord: ...


class ReviewRepositoryConflict(RuntimeError):
    """Raised when persistence observes a stale review version."""


class InMemoryReviewRepository:
    """Deterministic repository adapter used by local service and tests."""

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], ReviewRecord] = {}

    def get(self, tenant_id: str, review_id: str) -> ReviewRecord:
        try:
            return self._records[(tenant_id, review_id)]
        except KeyError as error:
            raise KeyError(review_id) from error

    def list(self, tenant_id: str) -> tuple[ReviewRecord, ...]:
        return tuple(
            record
            for (record_tenant, _), record in self._records.items()
            if record_tenant == tenant_id
        )

    def save(
        self, tenant_id: str, record: ReviewRecord, *, expected_version: int | None
    ) -> ReviewRecord:
        key = (tenant_id, record.review_id)
        current = self._records.get(key)
        if expected_version is None:
            if current is not None:
                raise ReviewRepositoryConflict(f"review already exists: {record.review_id}")
        elif current is None or current.version != expected_version:
            raise ReviewRepositoryConflict(f"stale review version: {record.review_id}")
        self._records[key] = record
        return record
