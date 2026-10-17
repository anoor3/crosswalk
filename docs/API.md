# Local API

The local API exposes `/health`, `/ready`, `/version`, and `/info` using the shared contract models. `POST /jobs` accepts a tenant and job kind and returns a queued local job response. These endpoints are operational checks and service seams, not the future mapping workspace UI.

`/info` reports the service name, configured version, and environment. The application defaults to the local environment and accepts explicit values during composition.

Every response receives an `X-Trace-Id` header. Callers may provide that header; otherwise the API generates a request-local identifier.

Invalid job payloads are rejected at the HTTP boundary with a 422 response. Shared Pydantic contracts reject missing, blank, and unknown fields before service execution.

The composition details are documented in [`service-boundary.md`](service-boundary.md).
