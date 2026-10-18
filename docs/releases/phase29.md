# Phase 29 release notes

Phase 29 adds local API request hardening: browser security headers, bounded request parsing, route method coverage, and policy contract tests.

The request limit is one mebibyte and rejects malformed size metadata conservatively.

Security middleware runs for successful, not-found, validation-error, and oversized responses.
