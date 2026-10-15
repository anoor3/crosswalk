from crosswalk_drift import DriftKind, detect_drift, schema_fingerprint


def test_detect_drift_classifies_schema_changes() -> None:
    before = {"properties": {"lossDt": {"type": "string"}, "amount": {"type": "number"}}}
    after = {"properties": {"loss_date": {"type": "string"}, "amount": {"type": "string"}}}
    events = detect_drift(before, after)
    assert {event.kind for event in events} == {
        DriftKind.REMOVED_FIELD,
        DriftKind.ADDED_FIELD,
        DriftKind.TYPE_CHANGED,
    }


def test_schema_fingerprint_is_order_independent() -> None:
    assert schema_fingerprint({"b": 2, "a": 1}) == schema_fingerprint({"a": 1, "b": 2})
