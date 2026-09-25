# Crosswalk — Product Definition (Phase 0)

> **Status:** Phase 0 deliverable (PLANNER §13).
> **Purpose:** Define exactly what is being built before implementation, so that
> every later phase can be checked against a fixed, honest description of the
> product. This document contains no invented metrics and no marketing claims
> (CHECKER §11 metric-honesty gate, §43 README-honesty gate).

---

## 1. One-line product definition

**Crosswalk helps an engineer connect an unfamiliar external API to their
company's canonical data model** — by discovering the API, profiling its real
field data, proposing field and enum mappings with explicit evidence and
confidence, letting a human resolve anything ambiguous, generating a typed
adapter plus tests, and later detecting schema drift and proposing
regression-tested repairs.

If a feature does not make integrations faster, safer, easier to understand,
easier to test, easier to deploy, easier to maintain, or easier to repair, it
is out of scope until that changes.

---

## 2. The 30-second explanation (exit criterion)

> A new customer's API returns claim data in a shape we've never seen. Instead
> of an engineer reading docs and hand-writing a mapping and adapter over days,
> Crosswalk reads the API, looks at real sample values, and proposes how each
> external field maps onto our clean internal `Claim` model — showing its
> evidence and confidence for each guess. Anything it isn't sure about (for
> example, an ambiguous money field) it flags for a human instead of guessing.
> Once a human confirms, Crosswalk generates the adapter code and tests. If the
> customer later changes their API, Crosswalk notices, explains what changed,
> and proposes a tested fix for a human to approve.

A new engineer who reads the paragraph above can accurately describe Crosswalk.
That is the Phase 0 exit criterion.

---

## 3. Primary persona

**Sarah — Forward Deployed / Integration Engineer** at an enterprise software
company.

Her company has a clean internal `Claim` model. Every new enterprise customer
exposes claim data through a *different* API — different field names, nesting,
enum codes, date formats, and relationships across endpoints. Sarah's job is to
reconcile each new external API with the internal model, prove the mapping is
correct, ship an adapter, and keep it working as the customer's API evolves.

Secondary users (same core workflow, different emphasis): backend engineers,
solutions engineers, platform engineers, founding engineers, SaaS
implementation and enterprise onboarding teams, and technical customer-success
engineers.

---

## 4. Problem statement

Enterprise APIs do not speak the same language. One system calls it `claim_id`,
another `lossNo`, another `caseRef`, another `incident.claimReference` — all the
same business concept. On top of naming, APIs differ in nesting, endpoint
structure, enum values, date formats, relationships, object IDs, pagination,
authentication, rate limits, optional fields, null semantics, deprecated
fields, undocumented behavior, incorrect documentation, and schema evolution
over time.

Today an engineer does this by hand: read docs → explore endpoints →
understand relationships → decode field meanings → map external → internal →
translate enums → write transform + adapter code → add auth/pagination/retry →
write tests → test against sandbox → deploy → monitor → repair when the
customer changes the API. It is slow, error-prone, and has to be repeated for
every customer.

---

## 5. User journey

### 5.1 New integration

```text
Customer API / OpenAPI / docs / sandbox
        │
        ▼
     DISCOVER   ── parse the API into a normalized internal catalog (deterministic)
        │
        ▼
     PROFILE    ── measure real field data: types, null rate, uniqueness, patterns
        │
        ▼
      MAP       ── propose field mappings with evidence + confidence + alternatives
        │
        ▼
    VALIDATE    ── check candidate mappings against observed data
        │
        ▼
  HUMAN REVIEW  ── engineer confirms / corrects / rejects / leaves unresolved
   (if needed)     (ambiguous fields never silently mapped)
        │
        ▼
 GENERATE ADAPTER ── typed adapter + transforms + enum maps + mapping.json
        │
        ▼
  GENERATE TESTS  ── contract/unit tests proving the mapping
        │
        ▼
   RUN SANDBOX    ── run the generated tests
        │
        ▼
 READY FOR REVIEW ── human sees results before anything ships
        │
        ▼
     DEPLOY
```

### 5.2 Existing integration (drift & repair)

```text
Integration running → customer changes API → Crosswalk detects drift
   → identifies likely replacement → generates repair candidate
   → regression tests run → human reviews diff + evidence
   → human approves → patch deployed
```

Default rule: **no automatic production patching** — a human always approves.

---

## 6. Inputs and outputs

### 6.1 Inputs (things a real user actually has)

- An OpenAPI / JSON-Schema spec, or documentation, or a sandbox endpoint.
- Sample response payloads (real or sandbox data).
- The company's canonical model (already defined internally).
- Optionally: API credentials for sandbox exploration (handled as secrets,
  never logged or committed — PLANNER §32).

### 6.2 Outputs (things that move the integration forward)

- A normalized API catalog (endpoints, fields, types, auth, pagination).
- Per-field value profiles.
- Mapping candidates, each with: external path, canonical target, confidence,
  evidence signals, alternatives, and a status
  (`CONFIRMED / HIGH_CONFIDENCE / REVIEW_REQUIRED / CONFLICTING / UNRESOLVED / REJECTED`).
- Enum mappings (with unseen-value handling).
- Cross-endpoint relationship hypotheses.
- Generated, inspectable adapter code + tests + `mapping.json`.
- Drift events (classified) and regression-tested repair candidates.

---

## 7. Initial canonical schema (implemented in Phase 1a)

```text
Claim
├── claim_id: str
├── incident_date: date
├── status: ClaimStatus            # OPEN | PENDING | CLOSED | REOPENED
├── claimant: Person
├── insured: Person
├── policy: Policy
└── financials: Financials
        ├── reserve: Decimal | None
        ├── payments: Decimal | None
        └── total_incurred: Decimal | None

Person
├── first_name: str
├── last_name: str
└── person_id: str | None

Policy
├── policy_number: str
├── effective_date: date | None
└── expiration_date: date | None
```

---

## 8. Initial fake external schemas (implemented in Phase 1b)

Three hand-written mock APIs express the *same* `Claim` concept with
increasing difficulty. Each has a **hidden ground-truth mapping** stored
separately from the API and never exposed to the inference system
(CHECKER §10 ground-truth integrity gate).

**Easy** — obvious names, ISO dates, clean status:
```json
{ "claimNumber": "C-100", "dateOfLoss": "2026-09-04", "status": "OPEN" }
```

**Medium** — abbreviations, US-format date, coded status:
```json
{ "lossNo": "C-100", "occDt": "09/04/26", "stateCd": "OPN" }
```

**Hard** — deep nesting, slashed date, numeric status code:
```json
{ "case": { "ref": "C-100", "incident": { "occurred_at": "2026/09/04" }, "state": 1 } }
```

---

## 9. Success metrics (measured, never invented)

Tracked from early phases; every number must be reproducible from a recorded
run with dataset, sample count, method, version, seed, and date (CHECKER §11).

**Quality:** field top-1 accuracy, field top-3 recall, enum accuracy,
relationship precision/recall, unsafe wrong-map rate, confidence calibration.

**Automation:** auto-resolved vs review-required mappings, average human
questions per integration.

**Generation:** adapters generated, generated-test pass rate, canonical
validation success rate.

**Drift:** injected changes, detected changes, repair proposals, correct
repairs, unsafe-repair-proposal rate.

**System:** p50/p95 latency, external call count, retry count, failure rate,
model tokens, estimated model cost.

**User outcome:** manual vs Crosswalk-assisted integration time, human
corrections, user-reported usefulness. (Populated only after real-user
validation in Phase 21 — never fabricated.)

---

## 10. Non-goals

Crosswalk is **not**: an insurance claims decision engine, a general-purpose
coding assistant, a generic document chatbot, a Postman replacement, a general
ETL platform, a no-code workflow builder, or an autonomous production
deployment agent with unlimited permissions.

---

## 11. Answers to the Phase 0 required questions (PLANNER §13)

1. **Who uses Crosswalk?** Forward Deployed / integration engineers (and
   adjacent backend/solutions/platform engineers) connecting external customer
   APIs to an internal canonical model.
2. **What work are they doing before Crosswalk?** Manually reading docs,
   exploring endpoints, decoding fields, hand-writing mappings, transforms,
   adapters, and tests, then maintaining them as the API changes.
3. **What input do they provide?** An external API spec/docs/sandbox + sample
   payloads + their canonical model (and optionally sandbox credentials).
4. **What output do they receive?** A normalized API catalog, field profiles,
   evidence-backed mapping candidates with status, enum maps, relationship
   hypotheses, and generated adapter code + tests — plus drift events and
   tested repair candidates over time.
5. **What manual work is removed?** The rote parts: structural parsing,
   statistical profiling, first-pass mapping proposals, boilerplate adapter and
   test generation, and drift detection.
6. **What risks remain human-controlled?** Confirming ambiguous or
   safety-sensitive mappings (e.g. financial fields), approving generated code,
   and approving any drift repair before it ships. Crosswalk proposes; humans
   decide.
7. **What can be measured?** All metrics in §9 — reproducibly, from recorded
   runs, with no fabricated numbers.

---

## 12. Product principles carried into every phase

- **Deterministic problems use deterministic code.** No LLM for parsing JSON,
  following `$ref`, computing null rate/uniqueness, comparing hashes, or
  validating types. AI is used only for semantics, ambiguity, conflicting docs,
  relationship hypotheses, and repair reasoning.
- **AI is a hypothesis generator, not truth.** Model output never becomes
  ground truth automatically; it is one evidence signal among many.
- **Never hide uncertainty.** Every mapping carries a status and may be left
  `UNRESOLVED`. Crosswalk is allowed to say "I don't know."
- **Metrics are real and reproducible.** No invented accuracy or speedups.
- **Generated code is untrusted until tested.** No embedded credentials, no
  arbitrary shell access, separated from handwritten code.
- **Security is never optional.** Secrets never logged/committed; tenant
  isolation enforced in the backend; user-supplied URLs are SSRF-checked;
  agents are read-only / sandbox-only by default.
