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


def test_persist_state(tmp_path: Path) -> None:
    from crosswalk_review import ReviewRecord, ReviewState

    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        value = ReviewRecord(
            review_id="r", external_path="$.id", candidate=candidate(), state=ReviewState.UNRESOLVED
        )
        repo.save("t", value, expected_version=None)
    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        assert repo.get("t", "r").state is ReviewState.UNRESOLVED
