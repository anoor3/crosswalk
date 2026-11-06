from crosswalk_review import (
    EvaluationExample,
    ReviewAction,
    ReviewActionType,
    ReviewRecord,
    ReviewState,
    ReviewSummary,
    ReviewWorkspace,
)

from crosswalk_mapping import MappingCandidate, canonical_fields


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

    def list_all(self, tenant_id: str) -> tuple[ReviewRecord, ...]:
        return self._workspace(tenant_id).list_all()

    def count(self, tenant_id: str) -> int:
        return len(self.list_all(tenant_id))

    def list_decided(self, tenant_id: str) -> tuple[ReviewRecord, ...]:
        return tuple(
            record for record in self.list_all(tenant_id) if record.state is not ReviewState.OPEN
        )

    def list_by_state(self, tenant_id: str, state: ReviewState) -> tuple[ReviewRecord, ...]:
        return self._workspace(tenant_id).list_by_state(state)

    def list_by_reviewer(self, tenant_id: str, reviewer_id: str) -> tuple[ReviewRecord, ...]:
        return self._workspace(tenant_id).list_by_reviewer(reviewer_id)

    def list_by_action(self, tenant_id: str, action: ReviewActionType) -> tuple[ReviewRecord, ...]:
        return self._workspace(tenant_id).list_by_action(action)

    def history(self, tenant_id: str, review_id: str) -> tuple[ReviewAction, ...]:
        return self._workspace(tenant_id).history(review_id)

    def summary(self, tenant_id: str) -> ReviewSummary:
        return self._workspace(tenant_id).summary()

    def evaluation_example(self, tenant_id: str, review_id: str) -> EvaluationExample | None:
        return self._workspace(tenant_id).evaluation_example(review_id)

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
