# Service boundary

`crosswalk-service` composes the storage and job seams without depending on HTTP. `ServiceContext` owns those dependencies, while small functions create tenant-scoped mappings and execute one queued job.

The local API composes this boundary with immutable `ServiceConfig`. Persistence and queue implementations remain replaceable for later hosted deployment.

Focused checks are available with `make test-service`, `make types-service`, and `make lint-service`.

The HTTP boundary applies security headers and a one MiB request limit before invoking service routes.

The local metrics registry and readiness value are explicit seams for later telemetry exporters and dependency probes.
