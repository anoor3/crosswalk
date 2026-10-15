from crosswalk_deploy import RollbackPlan, RollbackStatus


def test_rollback_requires_a_previous_release() -> None:
    plan = RollbackPlan(release_id="r2", previous_release_id="r1")
    assert plan.status is RollbackStatus.READY
    assert plan.execute().status is RollbackStatus.EXECUTED
