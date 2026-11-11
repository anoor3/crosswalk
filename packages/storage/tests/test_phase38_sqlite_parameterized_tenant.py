from pathlib import Path

from crosswalk_storage import SQLiteReviewRepository

from crosswalk_mapping import MappingCandidate, MappingStatus


def candidate() -> MappingCandidate:
    return MappingCandidate(
        external_path="$.id",
        canonical_path=None,
        score=0,
        status=MappingStatus.UNRESOLVED,
        evidence=None,
    )


def test_parameterized_tenant(tmp_path: Path) -> None:
    from crosswalk_review import ReviewRecord

    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        tenant = "tenant' OR 1=1 --"
        repo.save(
            tenant,
            ReviewRecord(review_id="r", external_path="$.id", candidate=candidate()),
            expected_version=None,
        )
        assert len(repo.list(tenant)) == 1 and repo.list("other") == ()
