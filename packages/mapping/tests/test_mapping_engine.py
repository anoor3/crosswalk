"""Safety contracts independent of the three fixture APIs and their answers."""

import pytest

from crosswalk_discovery import ExternalField, FieldType
from crosswalk_mapping import CanonicalField, MappingCandidate, MappingStatus, map_fields
from crosswalk_profiler import SemanticType, profile_fields


def field(name: str, data_type: FieldType = FieldType.STRING) -> ExternalField:
    return ExternalField(json_path=f"$.{name}", name=name, data_type=data_type, required=True)


def target(name: str, data_type: FieldType = FieldType.STRING) -> CanonicalField:
    return CanonicalField(path=f"record.{name}", name=name, data_type=data_type)


def test_obvious_custom_target_without_fixture_vocabulary() -> None:
    result = map_fields([field("warehouseLabel")], targets=[target("warehouse_label")])[0]
    assert result.canonical_path == "record.warehouse_label"
    assert result.status == MappingStatus.HIGH_CONFIDENCE
    assert result.evidence is not None
    assert result.score == result.evidence.score


def test_types_alone_never_identify_meaning() -> None:
    result = map_fields([field("opaque")], targets=[target("warehouse_label")])[0]
    assert result.status == MappingStatus.UNRESOLVED
    assert result.canonical_path is None
    assert result.alternatives[0].canonical_path == "record.warehouse_label"


def test_ties_preserve_all_alternatives_and_order_is_stable() -> None:
    targets = [target("label").model_copy(update={"path": f"record.{x}.label"}) for x in "cba"]
    result = map_fields([field("label")], targets=targets)[0]
    assert result.status == MappingStatus.REVIEW_REQUIRED
    assert [result.canonical_path, *(x.canonical_path for x in result.alternatives)] == [
        "record.a.label",
        "record.b.label",
        "record.c.label",
    ]
    assert map_fields([field("label")], targets=list(reversed(targets))) == (result,)


def test_financial_name_and_values_still_require_domain_validation() -> None:
    source = field("reserve", FieldType.NUMBER)
    money = target("reserve", FieldType.NUMBER).model_copy(
        update={"semantic_type": SemanticType.CURRENCY}
    )
    result = map_fields([source], profile_fields([{"reserve": 1700.25}], ["$.reserve"]), [money])[0]
    assert result.status == MappingStatus.REVIEW_REQUIRED
    assert any("Financial" in reason for reason in result.reasons)


def test_array_roles_not_invented() -> None:
    source = field("label").model_copy(update={"json_path": "$.locations[*].label"})
    result = map_fields([source], targets=[target("label")])[0]
    assert result.status == MappingStatus.REVIEW_REQUIRED
    assert any("Array" in reason for reason in result.reasons)


def test_incompatible_type_is_conflicting() -> None:
    result = map_fields(
        [field("warehouseLabel", FieldType.BOOLEAN)], targets=[target("warehouse_label")]
    )[0]
    assert result.status == MappingStatus.CONFLICTING


def test_mixed_observations_are_conflicting() -> None:
    source = field("warehouseLabel")
    profiles = profile_fields(
        [{"warehouseLabel": "west"}, {"warehouseLabel": 17}], [source.json_path]
    )
    result = map_fields([source], profiles, [target("warehouse_label")])[0]
    assert result.status == MappingStatus.CONFLICTING


def test_homogeneous_observations_can_contradict_schema() -> None:
    source = field("warehouseLabel")
    profiles = profile_fields([{"warehouseLabel": False}], [source.json_path])
    result = map_fields([source], profiles, [target("warehouse_label")])[0]
    assert result.status == MappingStatus.CONFLICTING


def test_unparseable_dates_need_review() -> None:
    source = field("arrivalDate")
    destination = target("arrival_date").model_copy(update={"semantic_type": SemanticType.DATE})
    profiles = profile_fields([{"arrivalDate": "soon"}], [source.json_path])
    result = map_fields([source], profiles, [destination])[0]
    assert result.status == MappingStatus.REVIEW_REQUIRED
    assert any("recognized date" in reason for reason in result.reasons)


def test_description_and_name_conflict_is_not_averaged_away() -> None:
    source = field("warehouseLabel").model_copy(update={"description": "Invoice delivery address"})
    destinations = [
        target("warehouse_label").model_copy(update={"description": "Warehouse location name"}),
        target("billing_address").model_copy(update={"description": "Invoice delivery address"}),
    ]
    result = map_fields([source], targets=destinations)[0]
    assert result.status == MappingStatus.CONFLICTING
    assert any("different targets" in reason for reason in result.reasons)


def test_all_null_samples_cannot_be_high_confidence() -> None:
    source = field("warehouseLabel")
    result = map_fields(
        [source],
        profile_fields([{"warehouseLabel": None}], [source.json_path]),
        [target("warehouse_label")],
    )[0]
    assert result.status == MappingStatus.REVIEW_REQUIRED


def test_unproven_enum_conversion_is_reviewed() -> None:
    result = map_fields(
        [field("status")],
        targets=[target("status").model_copy(update={"enum_values": ("OPEN", "CLOSED")})],
    )[0]
    assert result.status == MappingStatus.REVIEW_REQUIRED


def test_observed_enum_counterexample_overrules_schema_compatibility() -> None:
    values = ("OPEN", "CLOSED")
    source = field("status").model_copy(update={"enum_values": values})
    destination = target("status").model_copy(update={"enum_values": values})
    profiles = profile_fields([{"status": "PRIVATE-INVALID-VALUE"}], [source.json_path])
    result = map_fields([source], profiles, [destination])[0]
    assert result.status == MappingStatus.CONFLICTING
    assert "PRIVATE-INVALID-VALUE" not in result.model_dump_json()


def test_declared_optional_source_needs_absence_policy() -> None:
    source = field("warehouseLabel").model_copy(update={"required": False})
    assert (
        map_fields([source], targets=[target("warehouse_label")])[0].status
        == MappingStatus.REVIEW_REQUIRED
    )


@pytest.mark.parametrize("nullable", [False, True])
def test_optional_parent_propagates_absence_risk(nullable: bool) -> None:
    parent = ExternalField(
        json_path="$.claimant",
        name="claimant",
        data_type=FieldType.OBJECT,
        required=False,
        nullable=nullable,
    )
    child = ExternalField(
        json_path="$.claimant.firstName",
        name="firstName",
        data_type=FieldType.STRING,
        required=True,
    )
    destination = CanonicalField(
        path="claim.claimant.first_name",
        name="first_name",
        data_type=FieldType.STRING,
    )
    result = map_fields([parent, child], targets=[destination])[1]
    assert result.status == MappingStatus.REVIEW_REQUIRED
    assert any("absent" in reason for reason in result.reasons)


def test_required_nonnullable_parent_does_not_add_absence_risk() -> None:
    parent = ExternalField(
        json_path="$.claimant",
        name="claimant",
        data_type=FieldType.OBJECT,
        required=True,
        nullable=False,
    )
    child = ExternalField(
        json_path="$.claimant.firstName",
        name="firstName",
        data_type=FieldType.STRING,
        required=True,
    )
    destination = CanonicalField(
        path="claim.claimant.first_name",
        name="first_name",
        data_type=FieldType.STRING,
    )
    result = map_fields([parent, child], targets=[destination])[1]
    assert result.status == MappingStatus.HIGH_CONFIDENCE


@pytest.mark.parametrize(
    "description",
    [
        "Identifier of the policy associated with the claim.",
        "Not the claim identifier. Identifier of the policy.",
    ],
)
def test_misleading_identifier_name_is_not_high_confidence(description: str) -> None:
    source = field("claimId").model_copy(update={"description": description})
    result = map_fields([source])[0]
    assert result.status in (MappingStatus.REVIEW_REQUIRED, MappingStatus.CONFLICTING)


@pytest.mark.parametrize(
    ("name", "path"),
    [
        ("originalClaimId", "$.originalClaimId"),
        ("parentClaimId", "$.parentClaimId"),
        ("previousFirstName", "$.claimant.previousFirstName"),
        ("previousLastName", "$.insured.previousLastName"),
        ("previousIncidentDate", "$.previousIncidentDate"),
        ("claimId", "$.archive.claimId"),
    ],
)
def test_unmatched_business_qualifiers_need_review(name: str, path: str) -> None:
    source = field(name).model_copy(update={"json_path": path})
    result = map_fields([source])[0]
    assert result.status in (MappingStatus.REVIEW_REQUIRED, MappingStatus.UNRESOLVED)


def test_competing_source_fields_are_not_both_high_confidence() -> None:
    result = map_fields(
        [field("warehouseLabel"), field("warehouse_label")], targets=[target("warehouse_label")]
    )
    assert all(x.status == MappingStatus.REVIEW_REQUIRED for x in result)
    assert all(any("compete" in reason for reason in x.reasons) for x in result)


def test_containers_and_empty_targets_retained() -> None:
    sources = [field("address", FieldType.OBJECT), field("tags", FieldType.ARRAY), field("label")]
    results = map_fields(sources, targets=[])
    assert [x.external_path for x in results] == [x.json_path for x in sources]
    assert all(x.status == MappingStatus.UNRESOLVED for x in results)
    assert map_fields([], targets=[]) == ()


def test_duplicate_paths_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate external"):
        map_fields([field("label"), field("label")])
    with pytest.raises(ValueError, match="duplicate canonical"):
        map_fields([field("label")], targets=[target("label"), target("label")])


def test_profiles_cannot_be_silently_misattached() -> None:
    profiles = profile_fields([{"label": "west"}], ["$.label"])
    with pytest.raises(ValueError, match="must refer"):
        map_fields([field("other")], profiles)
    with pytest.raises(ValueError, match="keys must match"):
        map_fields([field("label")], {"$.other": profiles["$.label"]})
    with pytest.raises(ValueError, match="duplicate profile"):
        map_fields([field("label")], [profiles["$.label"], profiles["$.label"]])


def test_results_roundtrip_without_retaining_sensitive_samples() -> None:
    source = field("warehouseLabel")
    results = map_fields(
        [source],
        profile_fields([{"warehouseLabel": "PRIVATE-SAMPLE-8271"}], [source.json_path]),
        [target("warehouse_label")],
    )
    assert "PRIVATE-SAMPLE" not in results[0].model_dump_json()
    assert MappingCandidate.model_validate_json(results[0].model_dump_json()) == results[0]
    assert all(x.status not in (MappingStatus.CONFIRMED, MappingStatus.REJECTED) for x in results)
