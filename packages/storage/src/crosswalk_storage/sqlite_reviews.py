"""SQLite review persistence with transactional tenant/version guards."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from crosswalk_review import ReviewRecord, ReviewRepository, ReviewRepositoryConflict

_SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS review_records (
    tenant_id TEXT NOT NULL,
    review_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 0),
    payload TEXT NOT NULL,
    PRIMARY KEY (tenant_id, review_id)
);
"""


class SQLiteReviewRepository:
    """A durable adapter implementing the review repository contract."""

    def __init__(self, database: str | Path = ":memory:") -> None:
        self._connection = sqlite3.connect(str(database))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._migrate()

    def _migrate(self) -> None:
        with self._connection:
            self._connection.executescript(_SCHEMA)
            self._connection.execute(
                "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)", (1,)
            )

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> SQLiteReviewRepository:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @staticmethod
    def _decode(row: sqlite3.Row) -> ReviewRecord:
        return ReviewRecord.model_validate(json.loads(row["payload"]))

    def get(self, tenant_id: str, review_id: str) -> ReviewRecord:
        row = self._connection.execute(
            "SELECT payload FROM review_records WHERE tenant_id = ? AND review_id = ?",
            (tenant_id, review_id),
        ).fetchone()
        if row is None:
            raise KeyError(review_id)
        return self._decode(row)

    def list(self, tenant_id: str) -> tuple[ReviewRecord, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM review_records WHERE tenant_id = ? ORDER BY review_id",
            (tenant_id,),
        ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def save(
        self, tenant_id: str, record: ReviewRecord, *, expected_version: int | None
    ) -> ReviewRecord:
        payload = json.dumps(record.model_dump(mode="json"), sort_keys=True)
        with self._connection:
            current = self._connection.execute(
                "SELECT version FROM review_records WHERE tenant_id = ? AND review_id = ?",
                (tenant_id, record.review_id),
            ).fetchone()
            if expected_version is None:
                if current is not None:
                    raise ReviewRepositoryConflict(f"review already exists: {record.review_id}")
                self._connection.execute(
                    "INSERT INTO review_records(tenant_id, review_id, version, payload) "
                    "VALUES (?, ?, ?, ?)",
                    (tenant_id, record.review_id, record.version, payload),
                )
            else:
                if current is None or current["version"] != expected_version:
                    raise ReviewRepositoryConflict(f"stale review version: {record.review_id}")
                self._connection.execute(
                    "UPDATE review_records SET version = ?, payload = ? "
                    "WHERE tenant_id = ? AND review_id = ? AND version = ?",
                    (record.version, payload, tenant_id, record.review_id, expected_version),
                )
        return record

    def migration_version(self) -> int:
        row = self._connection.execute(
            "SELECT MAX(version) AS version FROM schema_migrations"
        ).fetchone()
        return int(row["version"] or 0)


def _repository_contract_check(repository: SQLiteReviewRepository) -> ReviewRepository:
    return repository
