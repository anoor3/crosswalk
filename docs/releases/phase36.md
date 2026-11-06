# Phase 36 release notes

Phase 36 adds operator-facing review queries. Review workspaces can filter by
state, reviewer, or action, expose immutable decision history, and produce a
tenant-scoped state summary. The API exposes these through review collection
filters, `/reviews/{review_id}/history`, and `/reviews/summary`.

The summary is derived from the in-memory review registry and is intentionally
deterministic. History endpoints return recorded evidence only; they do not
expose hidden reasoning or raw source payloads.
