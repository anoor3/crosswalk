"""Small offline Phase 4 benchmark; answers are read only after all inference.

Run from the repository root: ``uv run python tests/eval/baseline.py``.
The JSON report contains counts, paths, and fingerprints, never payload values.
This evaluates field-path selection/ranking, not transform or adapter correctness.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from crosswalk_discovery import FieldType, analyze_openapi
from crosswalk_mapping import MappingStatus, map_fields
from crosswalk_profiler import profile_fields

REPO_ROOT = Path(__file__).resolve().parents[2]
REPRODUCTION_COMMAND = "uv run python tests/eval/baseline.py"
_FILTER = re.compile(r"\[\?\(@\.\w+==(?:'[^']*'|\d+)\)\]")


class EvaluationError(ValueError):
    """Inputs are inconsistent; producing an accuracy number would be misleading."""


@dataclass(frozen=True)
class FixtureCase:
    api: str
    endpoint: str
    schema: str
    payloads: str
    truth: str


# Inference inputs are fixed independently of hidden annotations. In particular,
# the endpoint and field list are never selected by reading ground_truth.json.
FIXTURE_MANIFEST = (
    FixtureCase(
        "easy",
        "/claims/{claim_number}",
        "fixtures/schemas/easy/openapi.json",
        "fixtures/payloads/easy/claims.json",
        "fixtures/external_apis/easy/ground_truth.json",
    ),
    FixtureCase(
        "medium",
        "/losses/{loss_no}",
        "fixtures/schemas/medium/openapi.json",
        "fixtures/payloads/medium/claims.json",
        "fixtures/external_apis/medium/ground_truth.json",
    ),
    FixtureCase(
        "hard",
        "/cases/{ref}",
        "fixtures/schemas/hard/openapi.json",
        "fixtures/payloads/hard/claims.json",
        "fixtures/external_apis/hard/ground_truth.json",
    ),
)


@dataclass(frozen=True)
class Prediction:
    external_path: str
    selected: str | None
    ranked_targets: tuple[str, ...]
    status: str
    is_leaf: bool


@dataclass(frozen=True)
class InferenceResult:
    api: str
    payload_count: int
    predictions: tuple[Prediction, ...]
    input_sha256: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class TruthMapping:
    external_path: str
    canonical_path: str


@dataclass(frozen=True)
class Truth:
    api: str
    seed_version: str
    mappings: tuple[TruthMapping, ...]
    sha256: str


def _read_json(path: Path) -> tuple[Any, str]:
    try:
        raw = path.read_bytes()
        return json.loads(raw), hashlib.sha256(raw).hexdigest()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        # Do not interpolate parser exceptions: they can contain payload values.
        raise EvaluationError(f"Cannot read valid JSON from {path.name}") from error


def infer_case(root: Path, case: FixtureCase) -> InferenceResult:
    """Discover, profile, and materialize predictions without opening annotations."""
    spec, spec_hash = _read_json(root / case.schema)
    payloads, payload_hash = _read_json(root / case.payloads)
    if not isinstance(spec, dict) or not isinstance(payloads, list) or not payloads:
        raise EvaluationError(f"{case.api}: expected a schema object and nonempty payload list")
    endpoint = analyze_openapi(spec).endpoint("GET", case.endpoint)
    if endpoint is None or not endpoint.response_fields:
        raise EvaluationError(f"{case.api}: fixed detail endpoint has no discovered fields")
    fields = endpoint.response_fields
    profiles = profile_fields(payloads, (field.json_path for field in fields))
    candidates = map_fields(fields, profiles)
    expected = {field.json_path: field for field in fields}
    actual = [candidate.external_path for candidate in candidates]
    if (
        len(expected) != len(fields)
        or len(set(actual)) != len(actual)
        or set(actual) != set(expected)
    ):
        raise EvaluationError(
            f"{case.api}: mapper must preserve each discovered field exactly once"
        )
    predictions = []
    for candidate in candidates:
        ranking = tuple(
            ([candidate.canonical_path] if candidate.canonical_path is not None else [])
            + [alternative.canonical_path for alternative in candidate.alternatives]
        )
        predictions.append(
            Prediction(
                candidate.external_path,
                candidate.canonical_path,
                ranking,
                candidate.status.value,
                expected[candidate.external_path].data_type
                not in (FieldType.OBJECT, FieldType.ARRAY),
            )
        )
    return InferenceResult(
        case.api,
        len(payloads),
        tuple(predictions),
        ((case.schema, spec_hash), (case.payloads, payload_hash)),
    )


def load_truth(root: Path, case: FixtureCase) -> Truth:
    """Read annotations only in the post-inference scoring stage."""
    data, digest = _read_json(root / case.truth)
    if not isinstance(data, dict) or data.get("api") != case.api:
        raise EvaluationError(f"{case.api}: ground-truth API does not match the manifest")
    seed_version = data.get("seed_version")
    rows = data.get("field_mappings")
    if not isinstance(seed_version, str) or not isinstance(rows, list) or not rows:
        raise EvaluationError(f"{case.api}: annotations require a seed version and mappings")
    mappings = []
    for row in rows:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("external_path"), str)
            or not isinstance(row.get("canonical_path"), str)
        ):
            raise EvaluationError(f"{case.api}: invalid ground-truth mapping")
        external = row["external_path"]
        canonical = row["canonical_path"]
        if not external.startswith("$.") or not canonical.startswith("claim."):
            raise EvaluationError(f"{case.api}: invalid mapping path format")
        if "[?(" in _FILTER.sub("[*]", external):
            raise EvaluationError(f"{case.api}: unsupported annotation predicate")
        mappings.append(TruthMapping(external, canonical))
    if len({item.canonical_path for item in mappings}) != len(mappings):
        raise EvaluationError(f"{case.api}: duplicate canonical target in annotations")
    return Truth(case.api, seed_version, tuple(mappings), digest)


def _ratio(numerator: int, denominator: int) -> dict[str, int | float | None]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": numerator / denominator if denominator else None,
    }


def score_case(result: InferenceResult, truth: Truth) -> dict[str, Any]:
    """Score exact source/target pairs; wildcard relaxation is explicitly separate."""
    if result.api != truth.api or not truth.mappings:
        raise EvaluationError("Scoring needs matching APIs and nonempty annotations")
    predictions = {prediction.external_path: prediction for prediction in result.predictions}
    if len(predictions) != len(result.predictions):
        raise EvaluationError(f"{result.api}: duplicate predicted external path")
    if len({item.canonical_path for item in truth.mappings}) != len(truth.mappings):
        raise EvaluationError(f"{result.api}: duplicate canonical target in annotations")
    for prediction in result.predictions:
        if len(set(prediction.ranked_targets)) != len(prediction.ranked_targets):
            raise EvaluationError(f"{result.api}: duplicate target in a ranking")
        if prediction.selected is not None and (
            not prediction.ranked_targets or prediction.ranked_targets[0] != prediction.selected
        ):
            raise EvaluationError(f"{result.api}: selected target must lead the ranking")
        if prediction.status not in {status.value for status in MappingStatus}:
            raise EvaluationError(f"{result.api}: unknown mapping status")
        if prediction.status == MappingStatus.HIGH_CONFIDENCE and prediction.selected is None:
            raise EvaluationError(f"{result.api}: high-confidence prediction lacks a selection")
    for mapping in truth.mappings:
        normalized = _FILTER.sub("[*]", mapping.external_path)
        if normalized not in predictions:
            raise EvaluationError(f"{result.api}: annotated source was not discovered")

    direct = tuple(item for item in truth.mappings if not _FILTER.search(item.external_path))

    def hits(rows: Sequence[TruthMapping], *, top_k: int, wildcard: bool = False) -> int:
        count = 0
        for item in rows:
            path = _FILTER.sub("[*]", item.external_path) if wildcard else item.external_path
            prediction = predictions.get(path)
            if prediction is not None and item.canonical_path in prediction.ranked_targets[:top_k]:
                count += 1
        return count

    exact_pairs = {(item.external_path, item.canonical_path) for item in truth.mappings}
    selected_correct = sum(
        (prediction.external_path, prediction.selected) in exact_pairs
        for prediction in result.predictions
    )
    high = tuple(
        prediction
        for prediction in result.predictions
        if prediction.status == MappingStatus.HIGH_CONFIDENCE
    )
    high_correct = sum(
        (prediction.external_path, prediction.selected) in exact_pairs for prediction in high
    )
    leaves = tuple(prediction for prediction in result.predictions if prediction.is_leaf)
    counts = {
        "apis": 1,
        "payloads": result.payload_count,
        "discovered_fields": len(result.predictions),
        "discovered_leaf_fields": len(leaves),
        "ground_truth_targets": len(truth.mappings),
        "direct_targets": len(direct),
        "role_conditional_targets": len(truth.mappings) - len(direct),
        "high_confidence_predictions": len(high),
        "high_confidence_wrong": len(high) - high_correct,
    }
    metrics = {
        "exact_selected_mapping_accuracy": _ratio(selected_correct, len(truth.mappings)),
        "exact_top1_target_ranking": _ratio(hits(truth.mappings, top_k=1), len(truth.mappings)),
        "exact_top3_target_ranking": _ratio(hits(truth.mappings, top_k=3), len(truth.mappings)),
        "direct_top1_target_ranking": _ratio(hits(direct, top_k=1), len(direct)),
        "direct_top3_target_ranking": _ratio(hits(direct, top_k=3), len(direct)),
        "wildcard_top1_target_ranking_only": _ratio(
            hits(truth.mappings, top_k=1, wildcard=True),
            len(truth.mappings),
        ),
        "wildcard_top3_target_ranking_only": _ratio(
            hits(truth.mappings, top_k=3, wildcard=True),
            len(truth.mappings),
        ),
        "high_confidence_exact_precision": _ratio(high_correct, len(high)),
        "high_confidence_leaf_coverage": _ratio(sum(item.is_leaf for item in high), len(leaves)),
        "high_confidence_exact_target_recall": _ratio(high_correct, len(truth.mappings)),
    }
    return {
        "api": result.api,
        "counts": counts,
        "metrics": metrics,
        "status_counts_all_fields": dict(
            sorted(Counter(item.status for item in result.predictions).items())
        ),
        "status_counts_leaf_fields": dict(sorted(Counter(item.status for item in leaves).items())),
        "role_conditional_targets": [asdict(item) for item in truth.mappings if item not in direct],
    }


def aggregate(reports: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Micro-average counts, never average per-API percentages."""
    if not reports or len({report["api"] for report in reports}) != len(reports):
        raise EvaluationError("Aggregation needs nonempty reports for distinct APIs")
    counts = {key: sum(report["counts"][key] for report in reports) for key in reports[0]["counts"]}
    metrics = {
        key: _ratio(
            sum(report["metrics"][key]["numerator"] for report in reports),
            sum(report["metrics"][key]["denominator"] for report in reports),
        )
        for key in reports[0]["metrics"]
    }
    combined: dict[str, Any] = {"counts": counts, "metrics": metrics}
    for group in ("status_counts_all_fields", "status_counts_leaf_fields"):
        combined[group] = dict(
            sorted(sum((Counter(report[group]) for report in reports), Counter()).items())
        )
    return combined


def _software(root: Path) -> dict[str, Any]:
    git = shutil.which("git")
    revision: str | None = None
    dirty: bool | None = None
    if git is not None:
        try:
            # Fixed read-only commands; absolute executable, no shell or user input.
            revision = subprocess.run(  # noqa: S603
                [git, "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()
            dirty = bool(
                subprocess.run(  # noqa: S603
                    [git, "status", "--porcelain"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=5,
                ).stdout.strip()
            )
        except (OSError, subprocess.SubprocessError):
            pass
    source_paths = sorted(
        path
        for directory in (root / "packages", root / "tests" / "eval")
        for path in directory.rglob("*.py")
        if "__pycache__" not in path.parts
    )
    source_paths.extend(
        path for path in (root / "pyproject.toml", root / "uv.lock") if path.exists()
    )
    return {
        "git_revision": revision,
        "working_tree_dirty": dirty,
        "python": sys.version.split()[0],
        "packages": {
            name: version(name)
            for name in (
                "crosswalk-canonical",
                "crosswalk-discovery",
                "crosswalk-profiler",
                "crosswalk-mapping",
            )
        },
        "source_sha256": {
            str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(source_paths)
        },
    }


def run_benchmark(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Run the fixed dataset with a strict all-inference-before-any-answers boundary."""
    results = tuple(infer_case(root, case) for case in FIXTURE_MANIFEST)
    prediction_bytes = json.dumps([asdict(result) for result in results], sort_keys=True).encode()
    # All candidates across ALL APIs are now frozen. Nothing below calls a mapper.
    truths = tuple(load_truth(root, case) for case in FIXTURE_MANIFEST)
    reports = [score_case(result, truth) for result, truth in zip(results, truths, strict=True)]
    return {
        "benchmark": "phase4-fixed-development-fixtures-v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "reproduction_command": REPRODUCTION_COMMAND,
        "dataset": {
            "description": (
                "Three hand-written Phase 1 development APIs; not a held-out generalization set."
            ),
            "manifest": [asdict(case) for case in FIXTURE_MANIFEST],
            "seed_versions": {truth.api: truth.seed_version for truth in truths},
            "random_seed": None,
            "input_sha256": dict(pair for result in results for pair in result.input_sha256),
            "annotation_sha256": {
                case.truth: truth.sha256
                for case, truth in zip(FIXTURE_MANIFEST, truths, strict=True)
            },
        },
        "software": _software(root),
        "prediction_sha256": hashlib.sha256(prediction_bytes).hexdigest(),
        "method": {
            "unit": (
                "Ground-truth source/target field pair; four payloads inform each API's "
                "profiles, not separate mapping trials."
            ),
            "exact": (
                "Full annotated source path and canonical target must match; "
                "conditional selectors are never wildcard-equivalent."
            ),
            "selected": (
                "Uses the selected canonical_path (including review candidates); "
                "abstentions are misses. This does not imply approval."
            ),
            "ranking": (
                "Selected target followed by alternatives, or alternatives alone for "
                "abstentions; deterministic tie order is retained."
            ),
            "direct": (
                "Subset without role predicates, with its own explicit denominator; "
                "excluded predicates remain in full metrics."
            ),
            "wildcard": (
                "Diagnostic target ranking only: replace annotation predicates with [*]. "
                "This does not validate role selection or executable mappings."
            ),
            "high_confidence": (
                "Exact pair precision; leaf coverage counts HIGH_CONFIDENCE leaf predictions "
                "/ all discovered leaves; wrong includes unannotated source predictions."
            ),
            "aggregation": (
                "Micro-average by summing numerators and denominators; "
                "zero-denominator rates are null."
            ),
            "limits": (
                "No transform, enum conversion, relationship, adapter execution, "
                "probability calibration, or production generalization assessment."
            ),
        },
        "apis": reports,
        "combined": aggregate(reports),
    }


def main() -> int:
    try:
        report = run_benchmark()
    except EvaluationError as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
