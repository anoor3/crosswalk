# Phase 5 implementation plan

## Task: Versioned human review domain

### User problem
Baseline mapping intentionally leaves ambiguous fields for an integration
engineer. The engineer needs to resolve those candidates with evidence and a
record of who decided what, without editing JSON by hand.

### Goal
Provide the domain contract for opening a review, making one guarded decision,
retaining its history, and turning approved decisions into evaluation examples.

### Inputs and outputs

The workspace accepts an immutable `MappingCandidate` and a canonical target
vocabulary. It returns immutable `ReviewRecord` snapshots and, for confirmed or
corrected decisions, an `EvaluationExample` containing only the source path,
chosen target, review version, reviewer, and concise rationale.

### Behavior

- `CONFIRM` accepts the candidate's selected target.
- `CORRECT` requires a different target from the supplied vocabulary.
- `REJECT` and `LEAVE_UNRESOLVED` preserve no target.
- Every action increments the record version and is retained in history.
- A caller must provide the current version; stale writes fail without mutation.
- A decided record cannot be decided again.

The implementation is an in-memory service boundary. Durable storage, HTTP
authorization, and a graphical workspace are later increments built against
this contract.

### Security and failure handling

There are no network calls, credentials, payloads, or model traces. Reviewer IDs
and rationales are required; target paths are validated against the canonical
vocabulary; duplicate IDs, missing records, stale versions, and invalid action
shapes raise typed errors.

### Definition of done

The state machine, audit history, correction/export path, concurrency guard, and
invalid-transition behavior have unit coverage; full repository quality gates
pass; README and architecture docs identify the durable/UI boundary honestly.
