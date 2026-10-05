# Phase 4 implementation plan

## Task: Deterministic baseline field mapping

### User problem
An integration engineer has discovered an unfamiliar API and profiled sample
responses. They need inspectable target suggestions and a clear review queue,
without manually comparing every source field with the canonical model.

### Goal
Implement PLANNER §17 with a reusable mapper and reproduce its actual limitations
against the three Phase 1 APIs. Deterministic lexical/statistical methods suffice
for this baseline; no AI, model provider, HTTP service, or database is required.

### Inputs
One endpoint's discovered fields, optional matching value profiles, and scalar
canonical targets (derived from Claim by default, or supplied by the caller).

### Outputs
One immutable MappingCandidate per input field, with a proposed target or an
explicit unresolved result, weighted evidence, all ranked alternatives, status,
and review reasons. Scores describe heuristic support, not calibrated accuracy.

### Files likely touched
`packages/mapping/`, root workspace configuration and lockfile,
`tests/integration/test_mapping.py`, `tests/eval/`, README, and mapping/evaluation
documentation. Delivery increments: mapper plus unit tests; integration and
benchmark; measured results and documentation.

### Database changes
None. Persistence and human approval belong to subsequent phases.

### API contract
`map_fields(fields, profiles=(), targets=None) -> tuple[MappingCandidate, ...]`.
Profile sequences and path-keyed profile dictionaries are accepted. Fields must
belong to one endpoint; duplicate or mismatched paths raise ValueError.

### Algorithm / behavior
Normalize lexical terms; score name/path, description, type, and observed value
compatibility independently. Combine available evidence using documented fixed
weights. Rank deterministically and retain all alternatives. Route uncertain,
conflicting, financial, array, enum-conversion, and collision cases for review.
The mapper cannot produce CONFIRMED or REJECTED decisions. Financial figures
always need domain validation; value distributions cannot prove their meaning.

### Edge cases
Missing descriptions/profiles, all-null samples, unknown or mixed types,
nullable fields, containers, empty target catalogs, ties, unrelated identifiers,
contradictory descriptions, dates needing validation, and party role filters.

### Failure cases
Invalid result scores or inconsistent statuses fail model validation. Duplicate
input paths and profiles attached to the wrong field fail explicitly. Unsupported
canonical annotations fail rather than dropping fields. Incomplete semantic
understanding preserves review/unresolved outcomes.

### Security considerations
No network, credentials, arbitrary execution, or production writes. Candidate
evidence contains no raw sample values. Inference cannot import benchmark labels.
The evaluation runner materializes predictions before loading hidden answers.

### Tests
#### Unit
Evidence arithmetic and validation; target derivation; lexical/type/profile
signals; deterministic ties; uncertainty, conflict, and collision routing.
#### Integration
Discovery → profiling → mapping on all three real fixture APIs, retaining every
field, with repeatable serializable results.
#### Contract
Immutable structured results with validated score/evidence relationships; no
adapter execution is added in this phase.
#### Eval
Fixed input manifest, exact path-pair correctness, direct-field and conditional
field denominators, ranked alternatives, high-confidence precision/coverage,
wrong high-confidence counts, and review/unresolved counts.

### Metrics affected
Actual baseline ranking accuracy, selected-pair correctness, review load, and
unsafe high-confidence suggestions on the small development fixture set. This
is not held-out performance, calibrated confidence, or a generalization claim.

### Definition of done
Mapper and meaningful tests pass; fixtures stay unchanged; lint/type checks pass;
an independent CHECKER review has no unresolved blockers; benchmark results are
recorded with inputs, software identity, date, and reproduction command; README
accurately describes the completed phase and remaining limitations. This develops
the FDE mapping/review workflow and typed backend/evaluation engineering.
