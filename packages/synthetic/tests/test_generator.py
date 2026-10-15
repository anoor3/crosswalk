import pytest

from crosswalk_synthetic import generate_api


def test_seeded_generation_is_reproducible() -> None:
    assert generate_api(7, 3) == generate_api(7, 3)
    assert generate_api(7, 3).records[0]["claim_id"] == "clm_7_0"


def test_generation_bounds_record_count() -> None:
    with pytest.raises(ValueError, match="between"):
        generate_api(records=0)
