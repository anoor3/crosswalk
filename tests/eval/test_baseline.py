"""Metric denominators, abstention, source predicates, and evaluation integrity."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from . import baseline
from .baseline import (
    EvaluationError,
    InferenceResult,
    Prediction,
    Truth,
    TruthMapping,
    aggregate,
    score_case,
)


def _result(*predictions: Prediction, api: str = "test") -> InferenceResult:
    return InferenceResult(api, 4, tuple(predictions), ())


def _truth(*pairs: tuple[str, str], api: str = "test") -> Truth:
    return Truth(api, "test", tuple(TruthMapping(*pair) for pair in pairs), "unused")


def _prediction(
    path: str,
    selected: str | None,
    *,
    alternatives: tuple[str, ...] = (),
    status: str = "REVIEW_REQUIRED",
    leaf: bool = True,
) -> Prediction:
    targets = ((selected,) if selected is not None else ()) + alternatives
    return Prediction(path, selected, targets, status, leaf)


def test_wildcard_diagnostics_never_count_as_exact_role_mapping() -> None:
    result = _result(
        _prediction("$.id", "claim.claim_id", status="HIGH_CONFIDENCE"),
        _prediction(
            "$.people[*].name",
            "claim.claimant.first_name",
            alternatives=("claim.insured.first_name",),
        ),
        _prediction("$.people", None, status="UNRESOLVED", leaf=False),
    )
    truth = _truth(
        ("$.id", "claim.claim_id"),
        ("$.people[?(@.role=='CLMT')].name", "claim.claimant.first_name"),
        ("$.people[?(@.role=='INSD')].name", "claim.insured.first_name"),
    )
    report = score_case(result, truth)
    metrics = report["metrics"]
    assert report["counts"]["role_conditional_targets"] == 2
    assert len(report["role_conditional_targets"]) == 2
    assert metrics["exact_selected_mapping_accuracy"] == {
        "numerator": 1,
        "denominator": 3,
        "rate": 1 / 3,
    }
    assert metrics["exact_top3_target_ranking"]["numerator"] == 1
    assert metrics["direct_top1_target_ranking"]["denominator"] == 1
    assert metrics["wildcard_top1_target_ranking_only"]["numerator"] == 2
    assert metrics["wildcard_top3_target_ranking_only"]["numerator"] == 3
    assert report["status_counts_all_fields"]["UNRESOLVED"] == 1
    assert "UNRESOLVED" not in report["status_counts_leaf_fields"]


def test_unresolved_suggestions_affect_ranking_but_not_selection_or_precision() -> None:
    report = score_case(
        _result(
            _prediction(
                "$.id",
                None,
                alternatives=("claim.claim_id",),
                status="UNRESOLVED",
            )
        ),
        _truth(("$.id", "claim.claim_id")),
    )
    assert report["metrics"]["exact_selected_mapping_accuracy"]["numerator"] == 0
    assert report["metrics"]["exact_top1_target_ranking"]["numerator"] == 1
    assert report["metrics"]["high_confidence_exact_precision"] == {
        "numerator": 0,
        "denominator": 0,
        "rate": None,
    }
    assert report["metrics"]["high_confidence_leaf_coverage"]["rate"] == 0


def test_precision_penalizes_unannotated_source_and_coverage_keeps_all_leaves() -> None:
    report = score_case(
        _result(
            _prediction("$.id", "claim.claim_id", status="HIGH_CONFIDENCE"),
            _prediction("$.role", "claim.status", status="HIGH_CONFIDENCE"),
            _prediction("$.extra", None, status="UNRESOLVED"),
        ),
        _truth(("$.id", "claim.claim_id")),
    )
    assert report["counts"]["high_confidence_wrong"] == 1
    assert report["metrics"]["high_confidence_exact_precision"]["rate"] == 0.5
    assert report["metrics"]["high_confidence_leaf_coverage"] == {
        "numerator": 2,
        "denominator": 3,
        "rate": 2 / 3,
    }


def test_micro_aggregation_sums_denominators_and_does_not_average_api_rates() -> None:
    first = score_case(
        _result(_prediction("$.id", "claim.claim_id"), api="first"),
        _truth(("$.id", "claim.claim_id"), api="first"),
    )
    second = score_case(
        _result(
            _prediction("$.id", None, status="UNRESOLVED"),
            _prediction("$.status", None, status="UNRESOLVED"),
            api="second",
        ),
        _truth(("$.id", "claim.claim_id"), ("$.status", "claim.status"), api="second"),
    )
    combined = aggregate([first, second])
    assert combined["metrics"]["exact_selected_mapping_accuracy"]["rate"] == 1 / 3
    assert combined["counts"]["apis"] == 2
    assert combined["status_counts_all_fields"]["UNRESOLVED"] == 2
    assert combined["metrics"]["high_confidence_exact_precision"]["rate"] is None


@pytest.mark.parametrize(
    "case", ["duplicate_source", "duplicate_target", "missing_source", "empty_truth"]
)
def test_invalid_scoring_inputs_fail_instead_of_improving_denominators(case: str) -> None:
    prediction = _prediction("$.id", "claim.claim_id")
    result = _result(prediction)
    truth = _truth(("$.id", "claim.claim_id"))
    if case == "duplicate_source":
        result = _result(prediction, prediction)
    elif case == "duplicate_target":
        truth = _truth(("$.id", "claim.claim_id"), ("$.id2", "claim.claim_id"))
    elif case == "missing_source":
        truth = _truth(("$.missing", "claim.claim_id"))
    else:
        truth = _truth()
    with pytest.raises(EvaluationError):
        score_case(result, truth)


@pytest.mark.parametrize(
    "prediction",
    [
        Prediction(
            "$.id", "claim.claim_id", ("claim.claim_id", "claim.claim_id"), "REVIEW_REQUIRED", True
        ),
        Prediction("$.id", "claim.claim_id", ("claim.status",), "REVIEW_REQUIRED", True),
        Prediction("$.id", None, (), "HIGH_CONFIDENCE", True),
        Prediction("$.id", None, (), "invented-status", True),
    ],
)
def test_invalid_rankings_and_statuses_are_rejected(prediction: Prediction) -> None:
    with pytest.raises(EvaluationError):
        score_case(_result(prediction), _truth(("$.id", "claim.claim_id")))


def test_aggregation_rejects_empty_or_repeated_api_reports() -> None:
    with pytest.raises(EvaluationError):
        aggregate([])
    report = score_case(
        _result(_prediction("$.id", "claim.claim_id")),
        _truth(("$.id", "claim.claim_id")),
    )
    with pytest.raises(EvaluationError):
        aggregate([report, report])


@pytest.mark.parametrize(
    "data",
    [
        [],
        {"api": "wrong"},
        {"api": "test", "seed_version": "1", "field_mappings": []},
        {"api": "test", "seed_version": "1", "field_mappings": [{"external_path": 9}]},
        {
            "api": "test",
            "seed_version": "1",
            "field_mappings": [
                {"external_path": "$.rows[?(@.role>1)].name", "canonical_path": "claim.claim_id"},
            ],
        },
    ],
)
def test_malformed_annotations_are_rejected(tmp_path: Path, data: Any) -> None:
    (tmp_path / "truth.json").write_text(json.dumps(data))
    case = baseline.FixtureCase("test", "/unused", "unused", "unused", "truth.json")
    with pytest.raises(EvaluationError):
        baseline.load_truth(tmp_path, case)


def test_json_failure_message_does_not_expose_payload_values(tmp_path: Path) -> None:
    (tmp_path / "payload.json").write_text('"sensitive value" invalid')
    with pytest.raises(EvaluationError) as caught:
        baseline._read_json(tmp_path / "payload.json")
    assert "sensitive value" not in str(caught.value)


def test_inference_requires_the_manifest_endpoint() -> None:
    case = replace(baseline.FIXTURE_MANIFEST[0], endpoint="/does-not-exist")
    with pytest.raises(EvaluationError, match="fixed detail endpoint"):
        baseline.infer_case(baseline.REPO_ROOT, case)


def test_inference_rejects_silently_dropped_candidates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(baseline, "map_fields", lambda *_args: ())
    with pytest.raises(EvaluationError, match="preserve each discovered field"):
        baseline.infer_case(baseline.REPO_ROOT, baseline.FIXTURE_MANIFEST[0])


def test_real_benchmark_materializes_every_prediction_before_reading_any_answers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    completed: list[str] = []
    read_json = baseline._read_json
    infer_case = baseline.infer_case

    def guarded_read(path: Path) -> tuple[Any, str]:
        if path.name == "ground_truth.json":
            assert completed == [case.api for case in baseline.FIXTURE_MANIFEST]
        return read_json(path)

    def tracked_inference(root: Path, case: baseline.FixtureCase) -> InferenceResult:
        result = infer_case(root, case)
        completed.append(case.api)
        return result

    monkeypatch.setattr(baseline, "_read_json", guarded_read)
    monkeypatch.setattr(baseline, "infer_case", tracked_inference)
    report = baseline.run_benchmark()
    counts = report["combined"]["counts"]
    assert counts["apis"] == 3
    assert counts["payloads"] == 12
    assert counts["ground_truth_targets"] == 45
    assert counts["direct_targets"] == 33
    assert counts["role_conditional_targets"] == 12
    assert report["combined"]["metrics"]["exact_top3_target_ranking"]["denominator"] == 45
    assert sum(len(item["role_conditional_targets"]) for item in report["apis"]) == 12
    assert len(report["dataset"]["input_sha256"]) == 6
    assert len(report["dataset"]["annotation_sha256"]) == 3
    assert report["software"]["source_sha256"]
    assert report["prediction_sha256"]


def test_changing_answers_cannot_change_predictions(monkeypatch: pytest.MonkeyPatch) -> None:
    first = baseline.run_benchmark()
    load_truth = baseline.load_truth

    def wrong_answers(root: Path, case: baseline.FixtureCase) -> Truth:
        truth = load_truth(root, case)
        rotated = truth.mappings[1:] + truth.mappings[:1]
        return replace(
            truth,
            mappings=tuple(
                TruthMapping(source.external_path, target.canonical_path)
                for source, target in zip(truth.mappings, rotated, strict=True)
            ),
        )

    monkeypatch.setattr(baseline, "load_truth", wrong_answers)
    second = baseline.run_benchmark()
    assert first["prediction_sha256"] == second["prediction_sha256"]
