# Local API

The local API exposes `/health`, `/ready`, `/version`, and `/info` using the shared contract models. `POST /jobs` accepts a tenant and job kind and returns a queued local job response. These endpoints are operational checks and service seams, not the future mapping workspace UI.

`/info` reports the service name, configured version, and environment. The application defaults to the local environment and accepts explicit values during composition.

Every response receives an `X-Trace-Id` header. Callers may provide that header; otherwise the API generates a request-local identifier.

Invalid job payloads are rejected at the HTTP boundary with a 422 response. Shared Pydantic contracts reject missing, blank, and unknown fields before service execution.

The composition details are documented in [`service-boundary.md`](service-boundary.md).

Focused API checks are available with `make test-api`, `make types-api`, and `make lint-api`.

Security-focused middleware checks are available with `make test-security`.

Responses include `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Referrer-Policy: no-referrer`. Requests larger than 1 MiB are rejected before route parsing.
