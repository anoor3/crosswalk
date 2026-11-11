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


def test_list_multiple(tmp_path: Path) -> None:
    from crosswalk_review import ReviewRecord

    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        for name in ("a", "b", "c"):
            repo.save(
                "t",
                ReviewRecord(review_id=name, external_path="$.id", candidate=candidate()),
                expected_version=None,
            )
        assert len(repo.list("t")) == 3
