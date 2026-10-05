# Phase 4 baseline evaluation

Run the fixed, offline benchmark from the repository root:

```sh
uv run python tests/eval/baseline.py
```

The command writes a JSON report to standard output. To retain a run:

```sh
uv run python tests/eval/baseline.py > /tmp/crosswalk-baseline.json
```

This is a development-fixture measurement, not an estimate of performance on
unseen production APIs. The dataset consists of the three hand-written Phase 1
APIs, four sample claims per API, and 15 annotated canonical targets per API.
Those 12 payloads inform field profiles; they are not 12 independent mapping
trials. The scoring population is 45 annotated source/target field pairs.

## Inference and annotation separation

The fixed manifest in `tests/eval/baseline.py` specifies each schema, detail
endpoint, and payload file without consulting ground truth. Each schema passes
through discovery, every discovered field passes through profiling, and the
mapper receives only discovered fields and their profiles. All predictions for
all three APIs are materialized into immutable snapshots before the evaluator
opens any `ground_truth.json` file. Inference never receives annotation paths,
transforms, or expected canonical targets from those files.

Tests enforce this ordering, check that changing annotations leaves the
prediction fingerprint unchanged, and reject missing or duplicated predictions.
The evaluator also fails on inconsistent or malformed annotations rather than
silently reducing the denominator. This is an in-process evaluation boundary,
not an operating-system sandbox for an untrusted mapper.

## Metrics and denominators

Every reported rate includes its integer numerator and denominator. A rate with
a zero denominator is `null`, including precision when an API produces no
`HIGH_CONFIDENCE` candidates. Combined rates are micro-averages: sum counts
first, then divide. They are not averages of the three API percentages.

| Metric | Numerator | Denominator |
|---|---|---|
| Exact selected mapping accuracy | Selected source/target pairs exactly matching annotations | All 45 annotated targets |
| Exact top-1 / top-3 target ranking | Correct target in the first 1 / 3 suggestions at the exact annotated source path | All 45 annotated targets |
| Direct top-1 / top-3 target ranking | Same ranking check, restricted to annotations without a role predicate | 33 direct annotated targets |
| Wildcard top-1 / top-3 target ranking only | Correct target in the first 1 / 3 suggestions after replacing an annotation's role predicate with `[*]` | All 45 annotated targets |
| High-confidence exact precision | Exactly correct `HIGH_CONFIDENCE` source/target selections | All `HIGH_CONFIDENCE` predictions |
| High-confidence leaf coverage | Discovered leaf fields assigned `HIGH_CONFIDENCE` | All 41 discovered leaf fields, including unannotated fields |
| High-confidence exact target recall | Exactly correct `HIGH_CONFIDENCE` source/target selections | All 45 annotated targets |

Selected mapping accuracy counts `canonical_path`, including candidates still
requiring review. It does not imply human approval. A candidate that abstains
with `canonical_path=None` is a selection miss even when its suggestions rank
the right target first. Ranking uses the selected target followed by stored
alternatives; for abstentions it uses alternatives alone. The mapper's stable
tie ordering is retained without awarding all tied candidates first place.

The medium and hard fixtures each contain six role-conditional targets. For
example, an annotated source selects one person's name using a role predicate,
while discovery provides a wildcard path spanning all people. These are
different source paths. This phase cannot infer the required selectors, so all
12 conditional targets remain misses in exact metrics. The report lists these
12 annotated pairs explicitly; the direct-only denominator never replaces the
full denominator. Wildcard ranking only measures whether the relevant canonical
target appears among suggestions. It does not prove correct person selection,
a complete mapping, or an executable adapter.

High-confidence wrong counts include both incorrect targets and predictions
from sources with no exact annotation, including wildcard sources substituted
for role-filtered annotations. The report retains separate status counts for
all 54 discovered fields and for their 41 leaves; object and array containers
therefore remain visible without inflating leaf coverage.

## Reproduction and limits

Each report records the UTC timestamp, reproduction command, Git revision,
working-tree dirty flag, Python/package versions, SHA-256 hashes of inputs and
annotations, source-file hashes, and a fingerprint of materialized predictions.
It records the fixture seed version and a null random seed because these
hand-written fixtures and the inference pipeline use no randomness. File and
source hashes identify the exact inputs even for a run made before commit.
Timestamps and revision metadata may differ across reproductions; unchanged
inputs and inference code should reproduce counts and prediction fingerprints.

The report contains aggregate statistics and field paths. It does not serialize
sample payload values, profile samples, credentials, or raw parser errors.
The suite runs offline with no live API or model dependency.

Field-path accuracy does not evaluate enum conversions, date/decimal transforms,
relationship selection, generated adapters, or downstream business correctness.
The heuristic mapping scores are not calibrated probabilities. Even perfect
observed high-confidence precision on this small development set would not
establish calibration or guarantee correctness on unseen APIs. Broader held-out
benchmarking belongs to later phases.
