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


def test_json_payload(tmp_path: Path) -> None:
    from crosswalk_review import ReviewRecord

    value = ReviewRecord(
        review_id="r",
        external_path="$.name",
        candidate=candidate().model_copy(update={"external_path": "$.name"}),
    )
    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        repo.save("t", value, expected_version=None)
        assert repo.get("t", "r").external_path == "$.name"
