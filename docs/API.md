# Local API

The local API exposes `/health`, `/ready`, `/version`, and `/info` using the shared contract models. `POST /jobs` accepts a tenant and job kind and returns a queued local job response. These endpoints are operational checks and service seams, not the future mapping workspace UI.

`/info` reports the service name, configured version, and environment. The application defaults to the local environment and accepts explicit values during composition.
