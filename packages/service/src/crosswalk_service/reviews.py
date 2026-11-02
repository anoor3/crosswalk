from crosswalk_mapping import MappingCandidate, canonical_fields
from crosswalk_review import ReviewActionType, ReviewRecord, ReviewWorkspace


class ReviewRegistry:
    """Tenant-isolated review workspaces for local orchestration."""

    def __init__(self) -> None:
        self._workspaces: dict[str, ReviewWorkspace] = {}

    def _workspace(self, tenant_id: str) -> ReviewWorkspace:
        return self._workspaces.setdefault(tenant_id, ReviewWorkspace(canonical_fields()))

    def open(self, tenant_id: str, review_id: str, candidate: MappingCandidate) -> ReviewRecord:
        return self._workspace(tenant_id).open(review_id, candidate)

    def get(self, tenant_id: str, review_id: str) -> ReviewRecord:
        return self._workspace(tenant_id).get(review_id)

    def list_open(self, tenant_id: str) -> tuple[ReviewRecord, ...]:
        return self._workspace(tenant_id).list_open()

    def decide(
        self,
        tenant_id: str,
        review_id: str,
        *,
        action: ReviewActionType,
        reviewer_id: str,
        expected_version: int,
        rationale: str,
        canonical_path: str | None = None,
    ) -> ReviewRecord:
        return self._workspace(tenant_id).decide(
            review_id,
            action=action,
            reviewer_id=reviewer_id,
            expected_version=expected_version,
            rationale=rationale,
            canonical_path=canonical_path,
        )
