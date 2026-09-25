# Crosswalk — Architecture

> Deeper technical companion to the [README](../README.md). This document
> describes the parts that exist today (Phases 0–2) in detail, and sketches how
> the planned layers attach to them. It is kept honest: anything not yet built
> is labeled *planned*.

---

## 1. Guiding constraints

Two documents govern every design decision:

- [`PLANNER.md`](../PLANNER.md) — the master build plan (phases, data model,
  build order, task format).
- [`CHECKER.md`](../CHECKER.md) — the strict reviewer gate that each phase is
  self-reviewed against before it is considered done.

The constraints that shape the code most:

1. **Deterministic problems use deterministic code** (PLANNER §6.3, CHECKER §6).
   Parsing, `$ref` following, statistics, and schema diffing are mechanical and
   must not use an LLM.
2. **Uncertainty is explicit** (PLANNER §6.4, CHECKER §8/§14). The system records
   what it does not understand instead of guessing or dropping it.
3. **Ground truth never leaks into inference** (CHECKER §10).
4. **Typed failures over silent ones** (CHECKER §34).

---

## 2. Repository shape

A [uv](https://docs.astral.sh/uv/) workspace with two kinds of member:

- `packages/*` — dependency-light domain libraries, independent of HTTP/DB/UI.
- `apps/*` — runnable services (currently the mock external APIs).

Shared tooling (Ruff, mypy `strict`, pytest) is configured once in the root
`pyproject.toml` and inherited by every member, so the whole workspace is held
to one standard. `uv.lock` is committed for reproducible installs.

Workspace members are listed explicitly (not via a `packages/*` glob) so that
an empty, not-yet-implemented package directory can exist in the tree without
breaking `uv sync`. Each package is added to the member list in the phase that
implements it.

---

## 3. The canonical model (`crosswalk-canonical`)

The target of every mapping. Pydantic v2 models:

```text
Claim
├── claim_id: str                     (non-blank)
├── incident_date: date               (calendar date, not datetime)
├── status: ClaimStatus               (OPEN | PENDING | CLOSED | REOPENED)
├── claimant: Person
├── insured: Person
├── policy: Policy
└── financials: Financials

Person       { first_name, last_name, person_id? }
Policy       { policy_number, effective_date?, expiration_date? }
Financials   { reserve?, payments?, total_incurred? }   # Decimal, >= 0
```

Design choices and their reasons:

| Choice | Reason |
|--------|--------|
| `frozen=True` | A canonical object is a *result*; nothing downstream should mutate it. |
| `extra="forbid"` | A mapping that produces an unexpected field fails loudly instead of silently dropping data. |
| `Decimal` money with `ge=0` | Financial values must not carry binary float error, and are not meaningfully negative here. |
| `date` not `datetime` | Incident dates are calendar dates; date-*format* translation is the adapter's job. |
| Nested `Policy`/`Financials` | Groups related concepts and gives mappings clear dotted paths (`claim.financials.total_incurred`). |

The package ships a `py.typed` marker so downstream packages get full type
information.

---

## 4. The mock external APIs (`crosswalk-mock-apis`)

Three FastAPI apps that express the **same** four seed claims in three shapes:

| Difficulty | Field names | Dates | Status | Parties | Money |
|-----------|-------------|-------|--------|---------|-------|
| easy | obvious (`claimNumber`) | ISO `2026-09-04` | string `OPEN` | named `claimant`/`insured` | decimal strings |
| medium | abbreviated (`lossNo`) | US `09/04/26` | coded `OPN` | `partyInfo[]` w/ `roleCd` | floats (lossy) |
| hard | terse + nested (`case.ref`) | slashed `2026/09/04` | numeric `1` | `involved[]` w/ `roleType` | terse `ledger` |

A single deterministic seed set (`seed_data.py`) drives all three serializers,
so a given claim is the same business fact everywhere — the property a mapping
benchmark depends on. There is no randomness or clock, so fixtures regenerate
byte-for-byte.

### Ground-truth isolation

Each API's correct mapping (external path → canonical path, enum maps, date
formats) lives in `fixtures/external_apis/<difficulty>/ground_truth.json`. The
app code never imports or serves it. A contract test verifies these files are
genuinely correct by *executing* them (see §6), but nothing in the inference
path is ever allowed to read them.

---

## 5. Discovery (`crosswalk-discovery`)

`analyze_openapi(spec) -> ApiCatalog`. Deterministic structural parsing; no LLM.

### 5.1 Data model (`catalog.py`)

`ApiCatalog` is the normalized view: `endpoints`, `auth_schemes`,
`pagination_hints`, and `unsupported`. Each `Endpoint` carries its parameters,
flattened request/response `ExternalField`s, the success status the response
came from, and whether the response is a top-level collection. Every model is
frozen with `extra="forbid"`.

Two ideas are load-bearing:

- **Stable `json_path` on every field.** `$.claimant.firstName`,
  `$.partyInfo[*].roleCd`. Later phases refer to fields by this path.
- **`UnsupportedConstruct` entries.** Anything the parser can't fully model is
  recorded with a location and a type — never dropped (CHECKER §14).

### 5.2 `$ref` resolution (`refs.py`)

- `resolve_ref` walks a local JSON pointer (`#/...`) token by token, decoding
  RFC-6901 escapes (`~1`→`/`, `~0`→`~`) and percent-encoding, handling both
  dict keys and list indices.
- `follow` chases a chain of refs to the first concrete object, tracking a
  visited set to raise `RefResolutionError` on a cycle.
- External (file/URL) references, missing targets, and non-object targets all
  raise `RefResolutionError` — the local-only limitation is loud, not silent.

### 5.3 Schema flattening (`flatten.py`)

A recursive walk that emits one `ExternalField` per object/array/leaf, with the
correct `json_path`, and returns `(fields, unsupported)`.

Type normalization collapses OpenAPI dialects onto one `FieldType` vocabulary
and computes nullability from **either** 3.0 `nullable: true` **or** 3.1
`type: [..., "null"]` / `anyOf`-with-null. A genuine multi-schema `anyOf`/
`oneOf`, an `allOf` composition, a `$ref` cycle reached through nested
properties, and an open `additionalProperties` map are each recorded as an
`UnsupportedConstruct` — while still extracting whatever can be extracted, so
the catalog is useful even for imperfect specs.

Cycle handling deserves a note: `RefResolver.follow` only catches cycles inside
a *ref chain*. A self-referential object (`Node.next → Node`) resolves fine as
a single object; the cycle only appears when the flattener recurses into its
properties. So the flattener threads a `seen_refs` set down the descent path
and stops (recording the cycle) the moment it re-enters a ref already on that
path. This is why recursive schemas terminate instead of looping.

### 5.4 Endpoint / auth / pagination (`analyzer.py`, `pagination.py`)

`analyze_openapi` validates the document (dict + version + `paths`, else
`InvalidSpecError`), then per path × method builds an `Endpoint`: parameters
(path-level shared with operation-level), the `application/json` request body,
and the primary success response (`200`/`201` → other `2xx` → `default`),
flattening each and re-scoping every unsupported entry under an
endpoint-labeled location. `securitySchemes` become `AuthScheme`s. Pagination
is a deterministic name heuristic over query parameters (cursor / offset+limit
/ page-number) that always records which parameters triggered the hint.

---

## 6. Testing strategy

The suite is layered to match CHECKER §12:

- **Unit** — canonical model behavior; `$ref` resolver; schema flattener over
  synthetic schemas covering every branch; analyzer edge cases (enums, 3.0
  nullable, unions, cycles, auth, pagination, invalid specs).
- **Integration** — the mock APIs exercised in-process via
  `httpx.ASGITransport` (no bound port, no network → not flaky); `analyze_openapi`
  run over the real generated OpenAPI fixtures.
- **Contract** — the ground-truth harness applies each hidden mapping to real
  payloads and asserts a valid canonical `Claim` equal to the seed. This both
  proves Phase 1's exit criterion and keeps the ground truth honest, without
  ever exposing it to inference.

All fixtures are deterministic; regenerating them produces no diff.

---

## 7. How the planned layers attach

- **Profiler** consumes an `ApiCatalog` plus sample payloads and produces
  per-`json_path` value profiles (type, null rate, uniqueness, patterns).
- **Mapping** combines name/description/type/value-profile signals into
  `mapping_candidates` with evidence and a status; benchmarked against the
  hidden ground truth via the **evals** harness.
- **Adapters** turn approved mappings into typed, credential-free code plus
  generated tests; the **runtime** executes adapters with auth/retries/
  pagination; **drift** fingerprints schemas and classifies changes; repair
  proposes regression-tested patches for human approval.

Each attaches to the deterministic core without weakening the constraints in §1.
