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


def test_parameterized_review_id(tmp_path: Path) -> None:
    from crosswalk_review import ReviewRecord

    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        review_id = "r' OR 1=1 --"
        repo.save(
            "t",
            ReviewRecord(review_id=review_id, external_path="$.id", candidate=candidate()),
            expected_version=None,
        )
        assert repo.get("t", review_id).review_id == review_id
