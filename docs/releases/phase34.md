# Phase 34 release notes

Phase 34 adds a tenant-isolated human review API. Clients can open a validated mapping candidate, inspect its current review state, and append a version-checked decision with reviewer identity and rationale.

The API preserves the review domain's safety rules: unresolved and rejected decisions do not select targets, stale versions conflict, and opening a review never approves a mapping.
