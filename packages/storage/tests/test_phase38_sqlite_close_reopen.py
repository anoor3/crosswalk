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


def test_close_reopen(tmp_path: Path) -> None:
    from crosswalk_review import ReviewRecord

    path = tmp_path / "reviews.db"
    repo = SQLiteReviewRepository(path)
    repo.save(
        "t",
        ReviewRecord(review_id="r", external_path="$.id", candidate=candidate()),
        expected_version=None,
    )
    repo.close()
    with SQLiteReviewRepository(path) as reopened:
        assert reopened.get("t", "r").review_id == "r"
