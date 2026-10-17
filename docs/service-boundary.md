# Service boundary

`crosswalk-service` composes the storage and job seams without depending on HTTP. `ServiceContext` owns those dependencies, while small functions create tenant-scoped mappings and execute one queued job.

The local API composes this boundary with immutable `ServiceConfig`. Persistence and queue implementations remain replaceable for later hosted deployment.
