# Phase 4 baseline results

This is the recorded run of the fixed offline benchmark after commit
`f0700f7a01cb41aec52a75d3b523b9029e48a1bd`:

```text
uv run python tests/eval/baseline.py
generated_at_utc: 2026-10-05T21:41:25.339924+00:00
working tree: clean
```

The development set contains three hand-written APIs, 12 payloads, 54
discovered fields, 41 discovered leaves, and 45 annotated source/target pairs.
The 33 direct targets and 12 role-conditional targets are reported separately;
the conditional targets remain in the full denominator.

| Metric | Correct | Total | Rate |
|---|---:|---:|---:|
| Exact selected mapping | 29 | 45 | 64.44% |
| Exact top-1 ranking | 30 | 45 | 66.67% |
| Exact top-3 ranking | 31 | 45 | 68.89% |
| Direct top-1 ranking | 30 | 33 | 90.91% |
| Direct top-3 ranking | 31 | 33 | 93.94% |
| High-confidence exact precision | 6 | 6 | 100.00% |
| High-confidence leaf coverage | 6 | 41 | 14.63% |
| High-confidence exact target recall | 6 | 45 | 13.33% |

Wildcard ranking is diagnostic only: top-1 is 35/45 (77.78%) and top-3 is
43/45 (95.56%) after replacing role selectors with `[*]`. It does not prove
that a role-filtered mapping or executable adapter is correct. The six
high-confidence predictions had zero wrong predictions, but this small
development set does not establish calibration or production generalization.

The complete JSON report, including input/source hashes, status counts, and
per-API metrics, is generated at `/private/tmp/crosswalk-phase4-baseline-command-check.json`
when the command above is run; the temporary report is intentionally not a
repository artifact.
