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


def test_save_and_get(tmp_path: Path) -> None:
    with SQLiteReviewRepository(tmp_path / "reviews.db") as repo:
        repo.save(
            "t",
            __import__("crosswalk_review").ReviewRecord(
                review_id="r", external_path="$.id", candidate=candidate()
            ),
            expected_version=None,
        )
        assert repo.get("t", "r").review_id == "r"
