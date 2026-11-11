# Phase 38 release notes

Phase 38 adds a SQLite implementation of the review repository. Records and
decision history are stored as validated JSON snapshots behind a tenant and
review ID primary key. Writes use parameterized SQL and a transaction with an
optimistic version guard, while startup applies an idempotent schema migration.

The adapter is suitable for local durable deployments and remains behind the
same `ReviewRepository` protocol, so a hosted database can replace it later.
