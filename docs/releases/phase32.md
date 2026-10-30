# Phase 32 release notes

Phase 32 exposes tenant-scoped mapping persistence through the local API. Clients can create, read, and optimistically update mapping records using shared frozen contracts.

Cross-tenant reads are hidden, stale versions return a conflict, and the storage implementation remains an in-memory seam. Mapping inference and human review decisions remain separate domain steps so the API never treats persistence as approval.
