# Phase 7 baseline results

The relationship baseline is implemented and verified on the three existing
fixture shapes.

```text
full command: uv run pytest -q
tests: 330 passed
relationship fixture cases: 3
```

The integration cases confirm that party identifiers overlap across the easy,
medium, and hard payload representations. The scorer reports aggregate overlap
and cardinality and keeps the candidate reviewable when field-name evidence is
not strong enough for automatic confidence. Unrelated claim IDs remain
unresolved.

This is a deterministic development-fixture check, not a production relationship
precision/recall claim. The fixtures do not contain separate person or policy
endpoints, so a larger benchmark and durable relationship review are required
before publishing relationship-quality metrics.
