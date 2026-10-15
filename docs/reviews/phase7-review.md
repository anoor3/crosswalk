# Review: Phase 7 relationship discovery baseline

## Verdict

PASS WITH FOLLOW-UP

## Product value

Relationship hypotheses help an integration engineer connect external records
without treating field-name similarity as proof. The output is reviewable and
retains alternatives when targets compete.

## Correctness

The baseline computes value overlap, uniqueness, cardinality, normalized name
similarity, type compatibility, and concise reasons. It preserves unresolved
results and detects directed graph cycles.

## Testing

Tests cover one-to-one, one-to-many, many-to-one, many-to-many, empty/null and
nested inputs, privacy of aggregate results, ranking conflicts, missing target
samples, duplicate targets, graph cycles, invalid nodes, JSON round-trips, and
real party identifiers across fixture API shapes.

## Failure handling

Nested relationship values and missing target samples fail explicitly. Zero
overlap remains unresolved. Competing candidates retain alternatives rather than
being silently selected.

## Security

Raw identifiers never appear in `OverlapStats` or relationship evidence. The
package has no network, credential, shell, or production-write capability.

## Observability

Candidates include aggregate counts, rates, cardinality, signal scores, reasons,
status, and alternatives. Request/job telemetry belongs to later runtime work.

## Performance and cost

The baseline is local deterministic computation. It has no model or network
cost; large-scale indexing can be added after measurement.

## Architecture

Discovery connects profiler extraction to the domain scorer. The package remains
independent of HTTP, persistence, UI, and agent orchestration.

## AI / evaluation

AI is not needed for overlap, cardinality, or exact structural evidence. Later
semantic assistance may propose hypotheses but cannot replace value checks or
human review.

## Documentation

The phase plan, README status, architecture notes, and this review describe the
implemented boundary and remaining production limitations.

## Blocking issues

None for the deterministic baseline. Follow-up work should add durable graph
storage, relationship review actions, and measured precision/recall over a
larger benchmark.
