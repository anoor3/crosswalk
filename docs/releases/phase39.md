# Phase 39 release notes

Phase 39 wires durable review persistence into the API application factory.
`CROSSWALK_REVIEW_DATABASE` selects a SQLite file; when it is absent, local
tests and development keep the in-memory adapter. Startup applies the
repository migration, and the application lifespan closes the database cleanly.

SQLite connections are created for the API's worker-thread model, and all
repository queries remain parameterized and tenant-scoped. The public review
routes remain unchanged, so clients do not need a migration step.
