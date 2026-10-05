# Review: Phase 4 baseline field mapping

## Verdict

PASS WITH FOLLOW-UP

## Product value

The mapper reduces repetitive source-to-canonical comparison for an integration
engineer while keeping ambiguous work visible. It preserves containers and
unresolved fields, and routes financial, array, enum, optionality, collision,
and conflicting-evidence cases to review.

## Correctness

Scores are computed from named evidence signals with fixed weights. Candidate
models enforce score/evidence consistency, immutable results, valid statuses, and
unique alternatives. Target fields are derived from the canonical model rather
than fixture annotations. Optional parent presence is propagated to descendants.

## Testing

Unit tests cover signal arithmetic, target derivation, deterministic ties,
type/profile conflicts, dates, enums, containers, duplicate paths, collisions,
qualifiers, and optional parents. Integration tests run discovery → profiling →
mapping for all three fixtures. The offline evaluator tests annotation
separation, denominators, ranking, and aggregation.

## Failure handling

Invalid or mismatched paths raise typed validation errors. Unsupported or
ambiguous cases remain unresolved or review-required; no mapping is silently
approved. Missing profiles and mixed observations are handled explicitly.

## Security

The mapper has no network, credential, shell, or production-write capability.
Evidence excludes raw sample values. The benchmark materializes all predictions
before reading hidden annotations and does not serialize payloads.

## Observability

Candidate reasons, signal explanations, alternatives, statuses, and benchmark
hashes provide inspectable provenance. Production request/job telemetry is
outside this package and belongs to later runtime phases.

## Performance and cost

The baseline is local deterministic computation with no model calls or external
dependencies. No performance claim is made; later evaluation can measure larger
datasets and calibration.

## Architecture

Core mapping logic is independent of HTTP, UI, persistence, and model providers.
The package accepts discovered fields, profiles, and caller-supplied targets,
which keeps it reusable beyond the initial Claim model.

## AI / evaluation

AI is not needed for this deterministic baseline. The fixed development-fixture
benchmark reports exact and ranking metrics with explicit denominators, retains
all role-conditional targets, and labels wildcard diagnostics separately. It is
not a held-out generalization or calibration result.

## Documentation

The phase plan, architecture, README status, and evaluation methodology are
updated. Human review, enum/relationship workflows, adapter generation, and
production integration remain planned follow-ups.

## Blocking issues

None for Phase 4. Follow-up work is required before treating heuristic scores as
probabilities or using candidates as approved mappings.
