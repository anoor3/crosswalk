# Phase 37 release notes

Phase 37 adds a durable-ready repository seam for human review. The review
registry now persists immutable snapshots by tenant and review ID, restores
workspaces from a shared repository, and enforces optimistic version checks
when decisions are written.

The shipped adapter is deterministic and in memory. A database adapter can
implement the `ReviewRepository` protocol without changing review domain
models, service methods, or HTTP routes.
