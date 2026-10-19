# Phase 29 release notes

Phase 29 adds local API request hardening: browser security headers, bounded request parsing, route method coverage, and policy contract tests.

The request limit is one mebibyte and rejects malformed size metadata conservatively.

Security middleware runs for successful, not-found, validation-error, and oversized responses.

The focused `make test-security` target exercises the middleware without running unrelated packages.

Security policy constants are exported from `crosswalk_api` so adapters can share the same boundary contract.

Phase 29 is complete when the full repository gate passes alongside the focused security checks.

The next operational slice adds local metrics and an explicit readiness value without claiming hosted telemetry.

The focused `make test-observability` target covers counters, snapshots, and readiness seams.
