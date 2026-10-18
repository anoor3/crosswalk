from crosswalk_contracts import CreateJobRequest


def test_create_job_contract_serializes() -> None:
    value = CreateJobRequest(tenant_id="t1", kind="discover")

    assert value.model_dump() == {"tenant_id": "t1", "kind": "discover"}
