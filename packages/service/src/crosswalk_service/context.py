from crosswalk_jobs import InMemoryQueue
from crosswalk_storage import VersionedStore

from .job_registry import JobRegistry
from .reviews import ReviewRegistry


class ServiceContext:
    """Explicit dependencies for local application services."""

    def __init__(
        self,
        store: VersionedStore | None = None,
        queue: InMemoryQueue | None = None,
        jobs: JobRegistry | None = None,
        reviews: ReviewRegistry | None = None,
    ) -> None:
        self.store = store or VersionedStore()
        self.queue = queue or InMemoryQueue()
        self.jobs = jobs or JobRegistry()
        self.reviews = reviews or ReviewRegistry()
