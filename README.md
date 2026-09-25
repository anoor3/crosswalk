<div align="center">

# Crosswalk

**Connect an unfamiliar external API to your company's canonical data model — with evidence, not guesswork.**

Discover · Profile · Map · Review · Generate · Test · Monitor · Repair

[Problem](#the-problem) · [How it works](#how-it-works) · [Architecture](#architecture) · [Getting started](#getting-started) · [Testing](#testing--quality-gates) · [Status](#project-status) · [Roadmap](#roadmap) · [Security](#security-posture)

</div>

---

## The problem

Enterprise APIs do not speak the same language. One system calls a claim identifier `claim_id`, another `lossNo`, another `caseRef`, another `incident.claimReference` — all the same business concept. Beyond naming, APIs differ in nesting, endpoint structure, enum codes, date formats, cross-endpoint relationships, pagination, authentication, null semantics, deprecated fields, undocumented behavior, incorrect documentation, and schema evolution over time.

A Forward Deployed / integration engineer reconciling a new customer API to a clean internal model does this by hand today:

> read docs → explore endpoints → decode field meanings → map external → internal → translate enums → write transforms + adapter → add auth/pagination/retries → write tests → test against sandbox → deploy → monitor → repair when the customer changes the API.

It is slow, error-prone, and repeated for every customer.

**Crosswalk automates the mechanical parts of that lifecycle and surfaces the ambiguous parts for a human — never hiding uncertainty behind a confident-looking number.**

### A concrete example

A new customer returns claim data in a shape you've never seen:

```json
{
  "lossNo": "CLM-88291",
  "occDt": "09/04/26",
  "stateCd": "OPN",
  "partyInfo": [{ "roleCd": "CLMT", "firstNm": "John", "lastNm": "Smith" }],
  "polNum": "P-99122",
  "incurredAmt": 14200
}
```

Crosswalk reads the API, profiles real sample values, and proposes how each field maps onto your canonical `Claim` model — with evidence and confidence for each guess:

```text
lossNo       ─────────────────►  claim.claim_id          99%   CONFIRMED
occDt        ─────────────────►  claim.incident_date     98%   HIGH_CONFIDENCE
stateCd (OPN)─────────────────►  claim.status (OPEN)     97%   HIGH_CONFIDENCE
incurredAmt  ──────── ? ───────►  claim.total_incurred   72%   REVIEW_REQUIRED
                         ├──────►  claim.reserve          19%
                         └──────►  claim.payments          9%
```

Ambiguous fields (like a money value that could be several canonical targets) are flagged for a human rather than silently mapped. Once confirmed, Crosswalk generates a typed adapter and tests. If the customer later changes the API, Crosswalk detects the drift and proposes a regression-tested repair for a human to approve.

---

## Who it's for

The primary user is a **Forward Deployed / Integration Engineer** onboarding external customer APIs onto an internal canonical model. The same workflow serves backend, solutions, platform, and founding engineers, and SaaS implementation / enterprise onboarding teams.

See [`docs/product-definition.md`](docs/product-definition.md) for the full persona, problem statement, and success metrics.

---

## How it works

Crosswalk is built around one product flow. Each stage is a focused, independently testable package.

```text
 Customer API / OpenAPI / docs / sandbox
                │
                ▼
   ┌─────────  DISCOVER  ─────────┐   deterministic OpenAPI → normalized ApiCatalog
   │                              │
   ▼                              │
 PROFILE   observe real field data (types, null rate, uniqueness, patterns)
   │                              │
   ▼                              │
  MAP      propose mappings with evidence + confidence + alternatives
   │                              │
   ▼                              │
 VALIDATE  check candidates against observed data
   │                              │
   ▼                              │
 HUMAN REVIEW   engineer confirms / corrects / rejects / leaves unresolved
   │                              │
   ▼                              │
 GENERATE ADAPTER + TESTS   typed, inspectable, credential-free code
   │                              │
   ▼                              │
 RUN SANDBOX → READY FOR REVIEW → DEPLOY
                │
                ▼
        MONITOR → detect DRIFT → propose REGRESSION-TESTED REPAIR → human approves
```

### Design principles

These are enforced throughout the codebase and by the project's review gate ([`CHECKER.md`](CHECKER.md)):

- **Deterministic problems use deterministic code.** No LLM parses JSON, follows `$ref`, computes a null rate, or compares schema hashes. AI is reserved for genuinely semantic work — ambiguous field meanings, conflicting documentation, relationship hypotheses, and repair reasoning.
- **AI is a hypothesis generator, not truth.** Model output is one evidence signal among many; it never becomes ground truth automatically.
- **Uncertainty is never hidden.** Every mapping carries a status — `CONFIRMED`, `HIGH_CONFIDENCE`, `REVIEW_REQUIRED`, `CONFLICTING`, `UNRESOLVED`, `REJECTED` — and Crosswalk is allowed to say "I don't know" and ask a human.
- **Generated code is untrusted until tested.** It contains no credentials and no arbitrary shell access, and is kept separate from handwritten code.
- **Metrics are real and reproducible.** No invented accuracy figures or speedups; every published number must be reproducible from a recorded run.

---

## Architecture

Crosswalk is a Python monorepo managed as a [uv](https://docs.astral.sh/uv/) workspace. Domain logic lives in small, dependency-light `packages/*` that are independent of any web, database, or UI concern; runnable services live in `apps/*`.

```text
crosswalk/
├── apps/
│   └── mock_apis/          # 3 mock external APIs (easy/medium/hard) — stand-ins
│                           # for unfamiliar customer APIs, all serving the same
│                           # claims in deliberately different shapes
├── packages/
│   ├── canonical/          # the clean internal model (Claim/Person/Policy/Financials)
│   ├── discovery/          # OpenAPI → normalized ApiCatalog (deterministic)
│   ├── profiler/           # value profiling            (planned)
│   ├── mapping/            # baseline field mapping      (planned)
│   ├── agents/             # investigation agent         (planned)
│   ├── adapters/           # adapter generation          (planned)
│   ├── runtime/            # production integration runtime (planned)
│   ├── drift/              # schema-drift detection      (planned)
│   ├── evals/              # evaluation harness          (planned)
│   └── synthetic/          # synthetic API generator     (planned)
├── fixtures/
│   ├── schemas/            # generated OpenAPI specs per mock API
│   ├── payloads/           # generated sample payloads per mock API
│   └── external_apis/      # HIDDEN ground-truth mappings (never fed to inference)
├── tests/                  # unit / integration / contract / regression / eval
├── docs/                   # product definition, architecture, playbooks
├── PLANNER.md              # master build plan (source of truth)
├── CHECKER.md              # engineering quality gate (strict reviewer rules)
└── README.md
```

### Packages built so far

#### `crosswalk-canonical` — the internal target model

Pydantic v2 models representing the clean internal world every external API is mapped into: `Claim`, `Person`, `Policy`, `Financials`, and the `ClaimStatus` enum. Models are **frozen** (a canonical object is an immutable result), reject unknown fields (`extra="forbid"`, so a mapping bug surfaces loudly instead of dropping data), represent money as `Decimal` (never float), and use calendar `date` for incident dates. This package is dependency-light so every other package can import it safely.

#### `crosswalk-discovery` — OpenAPI → `ApiCatalog`

Turns an unfamiliar OpenAPI 3.0/3.1 document into a normalized, deterministic `ApiCatalog`. Purely structural — **no LLM**.

- **`refs.py`** — a `$ref` resolver over local JSON pointers (`#/components/schemas/…`) with RFC-6901 token decoding and **cycle detection**, so recursive schemas never infinite-loop. External or missing references raise a typed `RefResolutionError`.
- **`flatten.py`** — flattens any schema into an ordered list of `ExternalField`s, each with a stable `json_path` (`$.claimant.firstName`, `$.partyInfo[*].roleCd`). Handles nested objects, arrays, `required`, enums, `format`, both nullable dialects (OpenAPI 3.0 `nullable: true` **and** 3.1 `type: [..., "null"]` / `anyOf` including null), and multi-type unions. Constructs it cannot fully model (`allOf`, genuine `oneOf`/`anyOf` unions, `$ref` cycles, open `additionalProperties` maps) are recorded **explicitly** as `UnsupportedConstruct` entries — nothing is dropped silently.
- **`analyzer.py`** — `analyze_openapi(spec) → ApiCatalog`: validates the document, extracts endpoints (method, path, operation id, parameters, request/response fields, collection detection), authentication schemes, and pagination hints.
- **`pagination.py`** — deterministic hints (cursor / offset+limit / page-number) derived from query-parameter names, always recording which parameters triggered the hint.

#### `crosswalk-mock-apis` — three mock external APIs

Three FastAPI applications (`easy`, `medium`, `hard`) that serve the **same** seed claims in increasingly difficult shapes — obvious ISO-dated fields, abbreviated coded fields with `MM/DD/YY` dates and role-tagged party arrays, and deeply nested structures with numeric status codes. They stand in for real customer APIs during development and benchmarking.

Each API has a **hidden ground-truth mapping** stored under `fixtures/external_apis/` that is never imported by, served from, or fed to any inference path — a strict rule so the benchmark answer can never leak into the system being evaluated.

---

## Tech stack

| Area | Choice |
|------|--------|
| Language | Python 3.12+ |
| Modeling / validation | Pydantic v2 |
| Web (mock APIs) | FastAPI + Uvicorn |
| Packaging / workspace | uv (Hatchling build backend) |
| Lint + format | Ruff (incl. `flake8-bandit` security rules) |
| Type checking | mypy (`strict`) |
| Testing | pytest + pytest-asyncio + httpx |

Planned for later phases (per [`PLANNER.md`](PLANNER.md)): PostgreSQL + SQLAlchemy + Alembic, a background job queue, a model-provider abstraction with cost accounting, Docker, GitHub Actions CI/CD, one cloud (AWS or GCP), and OpenTelemetry-based observability. A Next.js/TypeScript frontend is planned once the core API product is proven.

---

## Getting started

### Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** (`brew install uv`, or see the uv docs)

### Install

```bash
git clone https://github.com/anoor3/crosswalk.git
cd crosswalk
uv sync --python 3.12          # creates .venv and installs the whole workspace
```

### Try discovery on a mock API

```bash
uv run python - <<'PY'
import json
from crosswalk_discovery import analyze_openapi

spec = json.load(open("fixtures/schemas/medium/openapi.json"))
catalog = analyze_openapi(spec)

print(catalog.title, catalog.openapi_version)
for endpoint in catalog.endpoints:
    print(f"  {endpoint.method:4} {endpoint.path}  (collection={endpoint.response_is_collection})")

item = catalog.endpoint("GET", "/losses/{loss_no}")
for field in item.response_fields:
    flags = " ".join(f for f, on in
                      [("required", field.required), ("nullable", field.nullable)] if on)
    print(f"    {field.json_path:32} {field.data_type} {flags}")
PY
```

### Run a mock API locally

```bash
uv run uvicorn crosswalk_mock_apis.easy:app --reload
# then open http://127.0.0.1:8000/docs
```

### Regenerate fixtures (deterministic)

```bash
uv run python -m crosswalk_mock_apis.export_fixtures
```

---

## Testing & quality gates

Every meaningful change is expected to pass three gates before it is committed:

```bash
uv run ruff check .                              # lint + security rules
uv run mypy packages apps tests conftest.py      # strict type checking
uv run pytest                                    # full test suite
```

The suite currently contains **118 tests** across unit, integration, and contract layers:

- **Canonical model** — construction, validation (blank IDs, unknown fields, bad enum, negative money), `Decimal`/date handling, immutability, JSON round-trip.
- **Mock APIs** — every endpoint exercised in-process via `httpx.ASGITransport` (no network → not flaky), including 404 paths and confirmation that the same claim is served in three genuinely different shapes.
- **Ground-truth correctness** — a harness applies each hidden mapping to real payloads and proves it reconstructs a valid canonical `Claim` equal to the seed, for all three APIs.
- **Discovery** — `$ref` resolution and cycle detection, schema flattening across every branch, and `analyze_openapi` over both the real fixtures and synthetic edge specs (enums, OpenAPI 3.0 `nullable`, `oneOf` unions, circular refs, auth schemes, pagination styles, invalid specs).

Tests avoid real network dependencies and use deterministic fixtures throughout.

---

## Project status

Crosswalk is built phase-by-phase against [`PLANNER.md`](PLANNER.md), with each phase reviewed against [`CHECKER.md`](CHECKER.md) before it is considered done. This is an actively developing project; the sections below describe exactly what exists today versus what is planned. **No performance or accuracy metrics are claimed until they can be measured and reproduced.**

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Product definition | ✅ Done |
| 1 | Canonical model + three mock APIs + hidden ground truth | ✅ Done |
| 2 | OpenAPI discovery → `ApiCatalog` | ✅ Done |
| 3 | Value profiling | ⏳ Planned |
| 4 | Baseline field mapping | ⏳ Planned |
| 5 | Human review workspace | ⏳ Planned |
| 6–10 | Enum mapping, relationships, agent, adapter + test generation (MVP) | ⏳ Planned |
| 11–24 | Synthetic benchmark, evaluation, drift, repair, runtime, DB, jobs, security, cloud, observability, real users, docs | ⏳ Planned |

---

## Roadmap

The near-term path to a minimum viable product:

1. **Value profiling** — compute per-field type, null rate, uniqueness, patterns, and identifier/currency/date detection from real samples, independent of any AI.
2. **Baseline mapping** — an inspectable, non-agentic mapper combining name, description, type, and value-profile signals, benchmarked against the hidden ground truth.
3. **Human review** — resolve ambiguity without editing JSON; reviewed mappings become evaluation examples.
4. **Enum mapping & relationships** — translate enum codes and infer cross-endpoint references.
5. **Adapter + test generation** — turn approved mappings into typed, tested, credential-free adapters (MVP boundary).

Beyond MVP: a synthetic API generator and evaluation harness (to make quality measurable and reproducible), schema-drift detection, regression-tested repair proposals, a production integration runtime, database hardening, background jobs, cloud deployment, and observability.

---

## Security posture

Security is treated as a first-class concern from the first commit, not a later phase:

- **Secrets are never committed or logged.** `.gitignore` blocks `.env` files, keys, and credential stores; every commit is checked before staging.
- **Generated code carries no credentials** and no arbitrary shell access, and is kept separate from handwritten code.
- **Ground-truth isolation.** Benchmark answers live outside the code that is being evaluated and are never fed into any inference path.
- **Typed failures over silent ones.** Discovery raises typed errors for unusable input and records anything it cannot model, rather than guessing.

Planned as the system grows: tenant isolation enforced in the backend, SSRF protection for user-supplied URLs, read-only / sandbox-only agent defaults with audited tool calls, and secret management via a cloud secret manager. See [`PLANNER.md` §32](PLANNER.md) and [`CHECKER.md` §21–§24](CHECKER.md).

---

## Honest limitations (today)

- This is an in-progress project. Only Phases 0–2 are implemented; profiling, mapping, the agent, adapter/test generation, drift, and deployment are **not built yet**.
- Discovery supports **local** OpenAPI references only; external-file/URL references are intentionally rejected with a clear error rather than partially supported.
- The mock APIs are hand-written stand-ins, not real customer systems; the large synthetic benchmark (Phase 11) does not exist yet.
- **No accuracy, speed, or "Nx faster" claims are made** because there is nothing measured to back them yet. Those numbers will appear only once the evaluation harness (Phase 12) can reproduce them.

---

## Repository conventions

- **Commits** are small and focused, each describing what changed and why, and reference the relevant `PLANNER`/`CHECKER` sections.
- **Every phase** must satisfy the phase-exit checklist in [`CHECKER.md` §48](CHECKER.md): the feature works, has tests, handles failures, considers security, records honest metrics, and keeps the demo path working.
- **Documentation** lives in `docs/`; [`docs/architecture.md`](docs/architecture.md) has the deeper technical walkthrough.

---

<div align="center">

Built to practice and demonstrate real end-to-end engineering — schema inference, statistical profiling, evidence-based mapping, agent design, evaluation, drift recovery, and production concerns — not to look impressive.

</div>
