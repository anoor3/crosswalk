import pytest

from crosswalk_runtime import RetryPolicy, retry_delay


def test_retry_delay_is_bounded_and_reproducible() -> None:
    policy = RetryPolicy(max_attempts=4, base_delay_seconds=1, max_delay_seconds=3, jitter_ratio=0)
    assert retry_delay(policy, 3, seed=4) == 3
    assert retry_delay(policy, 3, seed=4) == retry_delay(policy, 3, seed=4)


def test_retry_attempt_must_be_in_policy() -> None:
    with pytest.raises(ValueError, match="within policy"):
        retry_delay(RetryPolicy(max_attempts=2), 3)
