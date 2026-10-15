# Phase 7 implementation plan

## Task: Evidence-based relationship discovery

### User problem
External APIs often split related records across endpoints. A field such as
`partyRef` may point to a person record, but name similarity alone is unsafe.
Engineers need evidence about whether values overlap, how identifiers repeat,
and which competing targets remain plausible.

### Goal
Build a deterministic baseline that ranks cross-endpoint relationship
hypotheses and represents them as an inspectable graph.

### Inputs and outputs

Inputs are discovered field references, sample payloads, optional descriptions,
and candidate target fields. Outputs contain aggregate overlap statistics,
cardinality, name/type evidence, alternatives, a status, and graph edges.
Raw identifiers are used transiently and never retained in evidence.

### Rules

- Value overlap is evidence, not proof of identity.
- Empty or zero-overlap comparisons remain unresolved.
- Close competing targets become conflicting/review-required.
- Unknown endpoint references and malformed nested values fail explicitly.
- Graph cycles are detectable and remain explicit for later human review.

### Definition of done

The package has typed models/errors, privacy-safe overlap statistics, scoring,
ranking, graph cycle detection, profiler-path discovery, unit tests, real-fixture
integration tests, and full repository quality gates.
