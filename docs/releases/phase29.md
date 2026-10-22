# Phase 29 release notes

Phase 29 adds local API request hardening: browser security headers, bounded request parsing, route method coverage, and policy contract tests.

The request limit is one mebibyte and rejects malformed size metadata conservatively.

Security middleware runs for successful, not-found, validation-error, and oversized responses.

The focused `make test-security` target exercises the middleware without running unrelated packages.

Security policy constants are exported from `crosswalk_api` so adapters can share the same boundary contract.

Phase 29 is complete when the full repository gate passes alongside the focused security checks.

The next operational slice adds local metrics and an explicit readiness value without claiming hosted telemetry.

The focused `make test-observability` target covers counters, snapshots, and readiness seams.

The API factory accepts an injected metrics registry so tests and future adapters can own lifecycle and export decisions.

Readiness remains a pure local value until dependency probes are wired into the service context.

No hosted metrics, alerting, or dependency discovery is implied by these local seams.

The local API now exposes both request counters and structured request events for deterministic inspection.

The focused `make test-events` target covers the collector and HTTP boundary.

Event responses are validated through the shared transport contract.

The initial events response is deterministic because the request itself is recorded before route execution.

The next job lifecycle slice remains in-memory and deterministic; durable queues and hosted persistence are still future work.
