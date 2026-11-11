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


def test_update_payload(tmp_path: Path) -> None:
    from crosswalk_review import ReviewRecord

    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        value = ReviewRecord(review_id="r", external_path="$.id", candidate=candidate())
        repo.save("t", value, expected_version=None)
        changed = value.model_copy(
            update={
                "version": 1,
                "external_path": "$.name",
                "candidate": candidate().model_copy(update={"external_path": "$.name"}),
            }
        )
        assert repo.save("t", changed, expected_version=0).external_path == "$.name"
