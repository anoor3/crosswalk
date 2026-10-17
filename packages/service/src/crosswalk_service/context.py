from crosswalk_jobs import InMemoryQueue
from crosswalk_storage import VersionedStore


class ServiceContext:
    """Explicit dependencies for local application services."""

    def __init__(
        self, store: VersionedStore | None = None, queue: InMemoryQueue | None = None
    ) -> None:
        self.store = store or VersionedStore()
        self.queue = queue or InMemoryQueue()
