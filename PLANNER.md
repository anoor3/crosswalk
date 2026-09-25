# PLANNER.md
# Crosswalk — Master Build Plan for the Planner AI

> **Project name:** Crosswalk  
> **Category:** Enterprise API integration automation / Forward Deployed Engineering infrastructure  
> **Primary goal:** Build a production-grade system that can understand an unfamiliar enterprise API, map it into a company’s canonical data model, generate and validate an integration, monitor it after deployment, detect breaking API changes, and propose safe repairs for human approval.
>
> This file is the **main source of truth for the Planner AI**.  
> The Planner AI must use it to decide what to build, in what order, why it matters, how it should be tested, and when a phase is actually complete.

---

# 0. PLANNER AI ROLE

The Planner AI is responsible for:

- breaking the project into phases,
- choosing the next engineering task,
- protecting the project from feature creep,
- keeping architecture coherent,
- keeping work aligned with the real user problem,
- ensuring every important feature has a test strategy,
- requiring measurable outcomes instead of vague “AI works” claims,
- maintaining production-quality engineering standards,
- ensuring the project develops skills relevant to both Forward Deployed Engineer and Software Engineer/backend/platform roles.

The Planner AI is **not allowed** to treat Crosswalk as:

- a generic chatbot,
- a simple RAG demo,
- an “AI dashboard,”
- a field-renaming toy,
- a single hard-coded API mapper,
- a UI-first hackathon project,
- an LLM wrapper with no measurable engineering value.

---

# 1. ONE-SENTENCE PRODUCT DEFINITION

**Crosswalk helps engineers connect unfamiliar external APIs to their company’s internal data model by discovering the API, inferring mappings, validating those mappings against real data, generating integration code, testing the integration, monitoring it after deployment, detecting API drift, and proposing regression-tested repairs.**

Everything in this repository must support that sentence.

If a feature does not make integrations faster, safer, easier to understand, easier to test, easier to deploy, easier to maintain, or easier to repair, the Planner AI should strongly question whether that feature belongs.

---

# 2. PRIMARY USER

## 2.1 Main user persona

### Forward Deployed Engineer / Integration Engineer

Example:

Sarah is an FDE at an enterprise software company.

Her company has a clean internal model:

```text
Claim
├── claim_id
├── incident_date
├── status
├── claimant
├── insured
├── policy_number
├── reserve
├── payments
└── total_incurred
```

A new enterprise customer exposes:

```json
{
  "lossNo": "CLM-88291",
  "occDt": "09/04/26",
  "stateCd": "OPN",
  "partyInfo": [
    {
      "roleCd": "CLMT",
      "firstNm": "John",
      "lastNm": "Smith"
    }
  ],
  "polNum": "P-99122",
  "incurredAmt": 14200
}
```

Sarah normally has to:

1. Read API documentation.
2. Explore endpoints.
3. Understand data relationships.
4. Decode field meanings.
5. Map external fields to internal fields.
6. Translate enums.
7. Write transformation code.
8. Write adapter code.
9. Add pagination/auth/retry handling.
10. Write tests.
11. Test against sandbox data.
12. Deploy.
13. Monitor.
14. Fix the integration when the customer changes the API.

Crosswalk helps automate and accelerate that lifecycle.

---

# 3. SECONDARY USERS

Potential users include:

- Backend engineers
- Integration engineers
- Solutions engineers
- Platform engineers
- Founding engineers
- SaaS implementation teams
- Enterprise onboarding teams
- Technical customer success engineers
- AI companies integrating into customer infrastructure

---

# 4. CORE USER PROBLEM

Enterprise APIs do not speak the same language.

One company may use `claim_id`, another `lossNo`, another `caseRef`, and another `incident.claimReference`. These may all represent the same business concept.

The problem becomes significantly harder when APIs also differ in:

- nesting,
- endpoint structure,
- enum values,
- date formats,
- relationships,
- object IDs,
- pagination,
- authentication,
- rate limits,
- optional fields,
- null semantics,
- deprecated fields,
- undocumented behavior,
- incorrect documentation,
- schema evolution.

Crosswalk must help an engineer discover and reconcile those differences.

---

# 5. THE PRODUCT FLOW

## 5.1 New integration

```text
Customer API / OpenAPI / docs / sandbox
                 ↓
              DISCOVER
                 ↓
              PROFILE
                 ↓
               MAP
                 ↓
            VALIDATE
                 ↓
      HUMAN REVIEW IF NEEDED
                 ↓
        GENERATE ADAPTER
                 ↓
         GENERATE TESTS
                 ↓
          RUN SANDBOX
                 ↓
        READY FOR REVIEW
                 ↓
             DEPLOY
```

## 5.2 Existing integration

```text
Integration is running
        ↓
Customer changes API
        ↓
Crosswalk detects drift
        ↓
Crosswalk identifies likely replacement
        ↓
Crosswalk generates repair candidate
        ↓
Regression tests run
        ↓
Human reviews diff + evidence
        ↓
Human approves
        ↓
Patch deployed
```

---

# 6. PRODUCT PRINCIPLES

## 6.1 Human-first automation

Crosswalk should automate obvious work and surface ambiguity.

Bad:

```text
incurredAmt -> reserve
confidence 73%
done
```

Good:

```text
incurredAmt

Possible mappings:
1. total_incurred — 73%
2. reserve — 19%
3. payments — 8%

Why unresolved:
- field name is ambiguous
- values exceed reserve totals on 14.2% of records
- documentation conflicts with observed data

Action:
Human review required
```

## 6.2 AI is a hypothesis generator, not truth

LLM output must never automatically become ground truth.

Evidence may include:

- field names,
- field descriptions,
- data types,
- value patterns,
- null rate,
- uniqueness,
- distributions,
- endpoint context,
- sample records,
- documentation,
- cross-record relationships,
- API behavior,
- sandbox test results,
- LLM semantic reasoning.

## 6.3 Deterministic problems should use deterministic code

Do not use an LLM to parse JSON, parse OpenAPI references, check if a field exists, compute null rate, calculate uniqueness, compare hashes, detect exact schema differences, or validate data types.

Use AI only when semantics, ambiguity, incomplete documentation, or reasoning justify it.

## 6.4 Never hide uncertainty

Every mapping or relationship should have a status such as:

```text
CONFIRMED
HIGH_CONFIDENCE
REVIEW_REQUIRED
CONFLICTING
UNRESOLVED
REJECTED
```

## 6.5 Generated code must be inspectable

Crosswalk should generate artifacts such as:

```text
adapter.py
transforms.py
enum_maps.py
mapping.json
tests/
README.md
```

## 6.6 Metrics must be real

Never create fake portfolio metrics. Every public number should be reproducible.

---

# 7. NON-GOALS

Crosswalk is not:

- an insurance claims decision engine,
- a general-purpose coding assistant,
- a generic document chatbot,
- an API testing replacement for Postman,
- a general ETL platform,
- a no-code workflow builder,
- an autonomous production deployment agent with unlimited permissions.

---

# 8. STRALA FDE SKILL ALIGNMENT

Crosswalk should deliberately practice:

## End-to-end deployment ownership

```text
scope → connect → discover → map → test → deploy → monitor → repair
```

## Client environments / APIs
This is the core project.

## Agentic AI
Build an integration investigation agent with tools.

## Prompt engineering / model integration
Use models for semantic mapping, ambiguity analysis, documentation interpretation, relationship hypotheses, and repair reasoning.

## Blitz prototyping
Generate adapters quickly and iterate from customer-specific feedback.

## Client communication
Real user pilots should require understanding requirements, explaining uncertainty, requesting clarification, and communicating deployment limits.

## Business outcomes
Measure integration time, number of manual mappings, mapping accuracy, repair time, and human intervention rate.

## Playbooks
Create deployment and integration playbooks from lessons learned.

---

# 9. STRALA SWE SKILL ALIGNMENT

The project should deliberately practice:

- Python
- FastAPI
- production backend development
- relational database design
- migrations
- architecture
- API design
- distributed jobs
- retries
- idempotency
- caching
- rate limits
- Docker
- CI/CD
- cloud deployment
- observability
- testing
- performance
- security
- production failure handling

---

# 10. TECH STACK

## Frontend

Recommended:

```text
Next.js
TypeScript
React
```

## Backend

```text
Python 3.12+
FastAPI
Pydantic v2
SQLAlchemy
Alembic
```

## Database

```text
PostgreSQL
```

## Queue / jobs

Start simple. Later use Redis + Celery/RQ, or Temporal only if workflow complexity truly justifies it.

## AI

Use a provider abstraction with structured output, model selection, prompt versions, traceable model runs, and cost accounting.

## Infrastructure

```text
Docker
Docker Compose
GitHub Actions
AWS or GCP
```

Pick one cloud first.

## Observability

```text
structured JSON logs
OpenTelemetry
metrics
trace IDs
```

---

# 11. TARGET REPOSITORY STRUCTURE

```text
crosswalk/
│
├── apps/
│   ├── web/
│   ├── api/
│   └── worker/
│
├── packages/
│   ├── canonical/
│   ├── discovery/
│   ├── profiler/
│   ├── mapping/
│   ├── agents/
│   ├── adapters/
│   ├── runtime/
│   ├── drift/
│   ├── evals/
│   └── synthetic/
│
├── fixtures/
│   ├── schemas/
│   ├── payloads/
│   └── external_apis/
│
├── generated/
│   └── adapters/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── regression/
│   └── eval/
│
├── infra/
│   ├── docker/
│   └── terraform/
│
├── docs/
│   ├── architecture.md
│   ├── new-integration-playbook.md
│   ├── mapping-system.md
│   ├── evaluation-methodology.md
│   ├── drift-recovery.md
│   ├── production-deployment.md
│   ├── incident-response.md
│   └── security-model.md
│
├── PLANNER.md
├── CHECKER.md
└── README.md
```

---

# 12. CORE DATA MODEL

The schema may evolve, but these concepts should exist.

## customers

```text
id
name
created_at
updated_at
```

## canonical_models

```text
id
name
version
schema_json
created_at
```

## integrations

```text
id
customer_id
canonical_model_id
name
environment
status
created_at
updated_at
```

## api_sources

Represents OpenAPI files, JSON Schema, documents, and samples.

```text
id
integration_id
source_type
location
content_hash
version
created_at
```

## external_schemas

```text
id
integration_id
version
schema_json
fingerprint
observed_at
```

## endpoints

```text
id
external_schema_id
method
path
operation_id
description
auth_type
pagination_type
```

## external_fields

```text
id
endpoint_id
json_path
name
data_type
description
required
nullable
```

## field_profiles

```text
id
external_field_id
sample_count
null_rate
unique_rate
min_value
max_value
patterns_json
sample_values_json
distribution_json
```

## mapping_candidates

```text
id
integration_id
external_field_id
canonical_path
score
status
explanation_json
created_at
```

## mapping_evidence

```text
id
candidate_id
evidence_type
score
payload_json
```

## approved_mappings

```text
id
integration_id
external_field_id
canonical_path
transform_id
version
approved_by
approved_at
```

## enum_mappings

```text
id
approved_mapping_id
external_value
canonical_value
confidence
status
```

## relationship_candidates

```text
id
integration_id
source_field_id
target_endpoint_id
target_field_path
confidence
status
evidence_json
```

## agent_runs

```text
id
integration_id
goal
model
prompt_version
status
started_at
completed_at
estimated_cost
```

## tool_calls

```text
id
agent_run_id
tool_name
request_json
response_json
latency_ms
status
created_at
```

## test_runs

```text
id
integration_id
adapter_version
test_type
status
metrics_json
created_at
```

## drift_events

```text
id
integration_id
drift_type
old_schema_id
new_schema_id
severity
details_json
status
created_at
```

## patch_candidates

```text
id
drift_event_id
diff
confidence
evidence_json
test_run_id
status
approved_by
created_at
```

---

# 13. PHASE 0 — PRODUCT DEFINITION

## Goal
Define exactly what is being built before implementation.

## Deliverables

- product one-liner,
- primary persona,
- problem statement,
- user journey,
- initial canonical schema,
- initial fake external schema,
- success metrics,
- non-goals.

## Required questions

1. Who uses Crosswalk?
2. What work are they doing before Crosswalk?
3. What input do they provide?
4. What output do they receive?
5. What manual work is removed?
6. What risks remain human-controlled?
7. What can be measured?

## Exit criteria

A new engineer can explain the project accurately in under 30 seconds.

---

# 14. PHASE 1 — CANONICAL MODEL + MOCK APIS

## Goal
Create the clean internal world and several intentionally different external worlds.

## Canonical objects

Start with Claim, Person, Policy, and Financials.

Example:

```python
class Claim:
    claim_id: str
    incident_date: datetime
    status: ClaimStatus
    claimant: Person
    insured: Person
    policy_number: str
    reserve: Decimal | None
    payments: Decimal | None
    total_incurred: Decimal | None
```

## Build three hand-written fake APIs

### Easy

```json
{
  "claimNumber": "C-100",
  "dateOfLoss": "2026-09-04",
  "status": "OPEN"
}
```

### Medium

```json
{
  "lossNo": "C-100",
  "occDt": "09/04/26",
  "stateCd": "OPN"
}
```

### Hard

```json
{
  "case": {
    "ref": "C-100",
    "incident": {
      "occurred_at": "2026/09/04"
    },
    "state": 1
  }
}
```

## Requirements

- mock APIs built with FastAPI,
- OpenAPI generated,
- sample payloads available,
- hidden ground truth stored separately.

## Tests

- canonical validation,
- mock endpoint responses,
- deterministic fixtures,
- ground truth correctness.

## Exit criteria

- 3 running mock APIs,
- one canonical model,
- known machine-readable correct mapping for all three.

---

# 15. PHASE 2 — OPENAPI DISCOVERY

## Goal
Parse unfamiliar OpenAPI specifications into a normalized internal representation.

## Build

```python
analyze_openapi(spec) -> ApiCatalog
```

## Discover

- endpoints,
- HTTP methods,
- operation IDs,
- descriptions,
- request schemas,
- response schemas,
- nested fields,
- refs,
- arrays,
- enums,
- nullable,
- required fields,
- auth,
- pagination hints.

## Important rule
No LLM needed for structural parsing.

## UI
Show endpoint list, endpoint detail, response model, fields, and auth requirements.

## Tests

- OpenAPI 3.0,
- OpenAPI 3.1 where feasible,
- nested `$ref`,
- arrays,
- enums,
- oneOf/anyOf,
- missing descriptions,
- nullable differences.

## Exit criteria
Any supported OpenAPI file can be converted into a deterministic internal API catalog.

---

# 16. PHASE 3 — VALUE PROFILING

## Goal
Understand a field using actual observed data.

## For each field calculate

- data type,
- null rate,
- unique rate,
- sample values,
- min/max,
- mean where useful,
- string length,
- regex-like patterns,
- date detection,
- identifier detection,
- currency-like detection,
- enum candidate detection.

## Example

```text
lossNo

type: string
sample_count: 10,000
null_rate: 0%
unique_rate: 99.98%
pattern: CLM-[0-9]+
likely_type: identifier
```

## Requirements

- deterministic sampling where possible,
- safe handling of missing fields,
- safe handling of mixed types,
- no unnecessary sensitive payload logging.

## Exit criteria
A reusable profiler exists independent from the AI system.

---

# 17. PHASE 4 — BASELINE FIELD MAPPING

## Goal
Build a strong non-agentic baseline.

## Signals

1. Name similarity
2. Description similarity
3. Type compatibility
4. Value-pattern compatibility
5. Optional semantic model score

## Candidate output

```json
{
  "external_path": "$.lossNo",
  "canonical_path": "claim.claim_id",
  "score": 0.94,
  "status": "HIGH_CONFIDENCE",
  "alternatives": [],
  "evidence": {
    "name": 0.91,
    "description": 0.88,
    "type": 1.0,
    "value_profile": 0.97,
    "semantic": 0.95
  }
}
```

## Requirements

- scoring must be inspectable,
- no hard-coded fake confidence,
- unresolved candidates preserved,
- alternatives stored.

## Benchmark
Measure against Phase 1 ground truth.

## Exit criteria
Baseline accuracy is recorded and reproducible.

---

# 18. PHASE 5 — HUMAN REVIEW WORKSPACE

## Goal
Make ambiguity easy for an engineer to resolve.

## Core interaction

```text
EXTERNAL                         CANONICAL

lossNo       ─────────────────>  claim_id       99%
occDt        ─────────────────>  incident_date  98%
incurredAmt  ─────── ? ──────>  total_incurred 72%
                         ├────>  reserve        19%
                         └────>  payments        9%
```

## Clicking a mapping should show

- external path,
- external description,
- canonical candidate,
- example values,
- value profile,
- evidence signals,
- alternative candidates,
- confidence,
- source docs,
- confirm,
- reject,
- correct,
- leave unresolved.

## Requirements

- review action is versioned,
- reviewed mappings become evaluation examples,
- no hidden chain-of-thought display,
- show concise evidence/rationale instead.

## Exit criteria
A user can finish mapping review without editing JSON manually.

---

# 19. PHASE 6 — ENUM MAPPING

## Goal
Translate external enum values into canonical enum values.

Example:

```text
OPN -> OPEN
CLS -> CLOSED
RPN -> REOPENED
```

Harder:

```text
1 -> OPEN
2 -> PENDING
3 -> CLOSED
```

## Evidence

- docs,
- descriptions,
- transition behavior,
- correlations,
- examples,
- semantic inference.

## Rules

- preserve unknown values,
- never silently coerce an unseen enum,
- production unseen enum becomes a drift event.

## Metrics

- enum accuracy,
- unknown-value handling accuracy.

---

# 20. PHASE 7 — RELATIONSHIP DISCOVERY

## Goal
Understand relationships across endpoints.

Example:

```text
GET /losses/{id}
claimantRef = P882
```

Then:

```text
GET /people/P882
id = P882
firstNm = John
lastNm = Smith
```

Infer:

```text
loss.claimantRef
     ↓
people.id
     ↓
Claim.claimant
```

## Signals

- OpenAPI references,
- field naming,
- ID overlap,
- endpoint paths,
- cardinality,
- sample calls,
- semantic interpretation.

## Represent as graph

Node = endpoint/entity.  
Edge = foreign-key/reference relationship.

## Metrics

- relationship precision,
- relationship recall.

## Exit criteria
Crosswalk can map a canonical object using more than one endpoint.

---

# 21. PHASE 8 — INTEGRATION INVESTIGATION AGENT

## Goal
Turn passive mapping into an active investigation loop.

## Agent flow

```text
Goal
 ↓
Inspect API
 ↓
Create hypothesis
 ↓
Gather evidence
 ↓
Run test
 ↓
Resolve
 OR
Ask human
```

## Tools

Implement typed tools such as:

```python
inspect_openapi()
inspect_endpoint()
sample_records()
profile_field()
search_docs()
compare_fields()
inspect_relationship()
call_sandbox()
inspect_enum()
test_candidate_mapping()
```

Later:

```python
generate_adapter()
run_tests()
```

## Agent constraints

- explicit max iterations,
- timeout,
- model budget,
- cost budget,
- sandbox-only exploration by default,
- no production writes,
- every tool call audited.

## Output

- proposed mapping,
- evidence,
- confidence,
- unresolved questions,
- tool history,
- concise rationale.

## Evaluation

Compare baseline mapper vs agent-assisted mapper.

Measure:

- mapping accuracy,
- human review rate,
- cost,
- latency.

## Exit criteria
Keep the agent only if it adds measurable value.

---

# 22. PHASE 9 — ADAPTER GENERATION

## Goal
Turn approved mappings into usable code.

## Generated structure

```text
generated/
└── northstar/
    ├── adapter.py
    ├── transforms.py
    ├── enum_maps.py
    ├── models.py
    ├── mapping.json
    ├── README.md
    └── tests/
```

## Adapter responsibilities

- auth injection,
- endpoint calls,
- pagination,
- parsing,
- transformations,
- canonical validation,
- typed errors,
- clear interfaces.

## Requirements

- no credentials embedded,
- generated code formatted,
- generated code importable,
- generated code separated from handwritten code,
- generated code reviewable.

---

# 23. PHASE 10 — TEST GENERATION

## Goal
Every generated integration comes with proof.

## Generate tests for

- field mappings,
- enum conversions,
- date parsing,
- null cases,
- optional fields,
- malformed payloads,
- pagination,
- retries,
- rate limits,
- canonical model validation,
- relationship resolution,
- unknown fields.

## Contract test

```python
async def test_get_claim():
    claim = await adapter.get_claim("CLM-100")

    assert claim.claim_id == "CLM-100"
    assert claim.status == ClaimStatus.OPEN
```

## Exit criteria
No adapter can be marked ready before generated tests pass.

---

# 24. MVP BOUNDARY

The MVP ends here.

The MVP must prove:

```text
unknown API
 ↓
discover
 ↓
profile
 ↓
map
 ↓
human review
 ↓
generate adapter
 ↓
run tests
 ↓
canonical output
```

Do not delay the first usable version because future phases sound impressive.

---

# 25. PHASE 11 — SYNTHETIC API GENERATOR

## Goal
Create a large reproducible benchmark.

Start from the canonical schema and generate external variants.

## Transformations

- rename fields,
- abbreviate,
- use synonyms,
- random nesting,
- flatten objects,
- move fields,
- change date formats,
- change enum values,
- numeric enums,
- multiple endpoints,
- references,
- added irrelevant fields,
- null-heavy fields,
- duplicate concepts,
- misleading names,
- missing descriptions,
- incorrect descriptions.

## Difficulty levels

### Easy
Obvious names, simple structure, clean docs.

### Medium
Abbreviations, nesting, enum translation, multiple endpoints.

### Hard
Misleading names, sparse docs, indirect relationships, inconsistent formatting.

### Nightmare
Wrong docs, deprecated endpoints, ambiguous semantics, type inconsistencies, sparse samples, schema drift.

## Critical requirement
Ground truth must be stored but never exposed to the inference system.

## Exit criteria
At least 100 reproducible synthetic APIs with deterministic seeds.

---

# 26. PHASE 12 — EVALUATION HARNESS

## Goal
Make system improvement scientific.

## Field mapping metrics

- top-1 accuracy,
- top-3 recall,
- precision,
- unsafe wrong-map rate,
- review rate.

## Enum metrics

- enum mapping accuracy,
- unseen value handling.

## Relationship metrics

- precision,
- recall.

## Agent metrics

- accuracy improvement,
- human questions,
- tool calls,
- cost,
- latency.

## Adapter metrics

- generated tests passed,
- canonical validation success.

## Calibration

Confidence should be calibrated.

Example:

```text
Predicted confidence bucket: 90–100%
Observed accuracy: 96%

Predicted confidence bucket: 80–90%
Observed accuracy: 85%
```

## Store runs

```text
eval_runs/
├── run_001.json
├── run_001.csv
└── run_001_summary.md
```

## Exit criteria
Every claimed improvement can be reproduced from an eval run.

---

# 27. PHASE 13 — SCHEMA DRIFT DETECTION

## Goal
Detect when a customer API changes.

## Detect

- removed field,
- added field,
- likely rename,
- type change,
- enum expansion,
- enum removal,
- path move,
- nesting change,
- endpoint removal,
- endpoint replacement,
- auth change,
- pagination change,
- response shape change.

## Fingerprints

Store:

- normalized full-schema fingerprint,
- endpoint fingerprints,
- field fingerprints.

## Example

```text
Expected:
lossDt

Observed:
loss_date

Candidate:
lossDt -> loss_date

confidence: 99.2%
```

## Exit criteria
Drift events are versioned, classified, and inspectable.

---

# 28. PHASE 14 — AUTOMATIC REPAIR CANDIDATES

## Goal
Generate safe, tested repair proposals.

## Flow

```text
drift
 ↓
identify broken mapping
 ↓
find replacement candidate
 ↓
generate patch
 ↓
replay historical fixtures
 ↓
run tests
 ↓
compare behavior
 ↓
human approval
```

## Repair review screen

Show:

```diff
- raw["lossDt"]
+ raw["loss_date"]
```

Also show confidence, evidence, affected mappings, test count, failures, behavioral differences, and risk.

## Default rule
No automatic production patching. Human approval required.

## Metrics

- drift events injected,
- detected,
- candidate accuracy,
- correct repairs,
- unsafe repair proposal rate.

---

# 29. PHASE 15 — PRODUCTION INTEGRATION RUNTIME

## Goal
Develop serious backend/SWE depth.

Implement:

## Authentication

- API key,
- bearer token,
- OAuth2 where practical.

## Timeouts
Explicit timeouts on all external calls.

## Retries

- exponential backoff,
- jitter,
- retryable status policy.

## Rate limiting
Respect customer API limits and avoid abuse.

## Pagination
Support page number, cursor, and next-link styles.

## Caching
Only when semantically safe.

## Idempotency
Especially important for future write operations.

## Errors

Typed errors such as:

```text
AuthenticationError
RateLimitError
ExternalTimeout
SchemaMismatchError
CanonicalValidationError
MappingAmbiguityError
RelationshipResolutionError
StaleVersionError
```

## Exit criteria
Adapter runtime survives expected enterprise API failure modes.

---

# 30. PHASE 16 — DATABASE HARDENING

## Requirements

- Alembic migrations,
- primary keys,
- foreign keys,
- indexes,
- unique constraints,
- tenant ownership,
- version fields,
- transactional approvals.

## Important indexes

Consider:

- integration_id,
- customer_id,
- schema fingerprint,
- mapping status,
- drift status,
- created_at.

## Concurrency

Plan for:

- two engineers reviewing same mapping,
- two workers analyzing same schema,
- drift arriving during patch review.

Use optimistic locking or transactions where appropriate.

---

# 31. PHASE 17 — BACKGROUND JOBS / QUEUES

## Use jobs for

- API discovery,
- sandbox sampling,
- profiling,
- large eval runs,
- synthetic generation,
- adapter test runs,
- drift comparisons.

## Job model

```text
id
type
status
attempt_count
progress
created_at
started_at
completed_at
error
```

## Requirements

- retry policy,
- persistent error,
- idempotent reruns,
- visible progress.

---

# 32. PHASE 18 — SECURITY

## Secrets

Never log, commit, or embed credentials in generated code.

Use environment variables locally and a cloud secret manager later.

## Tenant isolation

All customer-owned resources must be tenant scoped.

## SSRF protection

If Crosswalk can call user-provided URLs:

- validate scheme,
- block unsafe local/private ranges unless intentionally authorized,
- inspect redirects,
- restrict outbound behavior where practical.

## Generated code safety

Generated code should not have arbitrary shell access.

## Agent permissions

Default:

```text
READ ONLY
SANDBOX ONLY
```

Write actions require explicit permission.

## Audit log

Record:

- mapping approvals,
- mapping corrections,
- agent actions,
- patch approvals,
- deployments,
- critical settings changes.

---

# 33. PHASE 19 — CLOUD DEPLOYMENT

## Goal
Crosswalk cannot remain localhost-only.

## CI/CD

```text
git push
 ↓
GitHub Actions
 ↓
lint
 ↓
unit tests
 ↓
integration tests
 ↓
eval smoke tests
 ↓
Docker build
 ↓
deploy
```

## Pick one cloud

Example AWS:

- ECS/Fargate,
- RDS PostgreSQL,
- S3,
- Secrets Manager,
- CloudWatch / OpenTelemetry.

Do not use every AWS service just for keywords.

## Environments

- local,
- staging,
- demo/production.

## Required

- HTTPS,
- health checks,
- migrations,
- secrets management,
- rollback plan.

---

# 34. PHASE 20 — OBSERVABILITY

## The system must answer

- Which integration is unhealthy?
- Which endpoint is failing?
- When did drift start?
- What is p95 latency?
- Are rate limits being hit?
- What agent runs are expensive?
- Which mappings require review?
- When was last successful run?

## Structured logs

Include:

```text
request_id
customer_id
integration_id
job_id
agent_run_id
endpoint
latency_ms
status
retry_count
schema_version
```

Never log secrets.

## Metrics

- request count,
- error rate,
- latency,
- retries,
- drift events,
- model calls,
- model cost,
- mapping review backlog.

---

# 35. PHASE 21 — REAL USER VALIDATION

## Goal
Get miniature FDE experience.

Find 1–3 real developers or teams.

Possible users:

- student startup,
- open-source project,
- small SaaS,
- developer friend,
- student organization with software.

Ask for:

```text
their desired internal schema
+
a real third-party API they need to consume
```

Observe:

- setup difficulty,
- incorrect mappings,
- confusing screens,
- undocumented API behavior,
- missing capabilities,
- human review time.

## Measure

- time to first working adapter,
- number of manual corrections,
- failed test count,
- mapping review count,
- integration completion time.

## Important
Never invent testimonials or results.

---

# 36. PHASE 22 — FDE DEPLOYMENT PLAYBOOK

Create `docs/new-integration-playbook.md`.

It should cover:

1. Customer discovery
2. Business objective
3. Canonical model
4. Sandbox access
5. Credential handling
6. API inventory
7. Schema analysis
8. Mapping review
9. Adapter generation
10. Contract testing
11. Shadow validation
12. Canary
13. Go-live
14. Monitoring
15. Incident response
16. Drift management
17. Customer handoff
18. Lessons learned

---

# 37. PHASE 23 — MULTIMODAL INPUT

Only after the core API product works.

Add support for:

- PDF docs,
- spreadsheet data dictionaries,
- architecture diagrams,
- screenshots.

Example conflict:

OpenAPI:

```text
incurredAmt: number
```

PDF:

```text
Total incurred is paid + outstanding reserve.
```

Spreadsheet:

```text
Source column: ReserveLedger.Total
```

Crosswalk should show the conflict.

---

# 38. PHASE 24 — FINAL PRODUCT POLISH

## Main visual idea

The center of the product should show transformation:

```text
EXTERNAL API                           CANONICAL MODEL

lossNo ─────────────────────────────> claim_id

occDt ──────────────────────────────> incident_date

party.claimantRef ──────┐
                        ▼
                 GET /people/{id}
                        │
                        └───────────> claimant

incurredAmt ──────────── ? ────────> total_incurred
                         ↑
                    REVIEW NEEDED
```

## Primary screens

1. New Integration
2. API Discovery
3. Mapping Workspace
4. Human Review
5. Relationship Explorer
6. Generated Adapter
7. Test Results
8. Integration Health
9. Drift Event
10. Repair Review
11. Evaluation Lab

## Avoid

- chat-first product,
- fake AI agent avatars,
- generic KPI-card dashboards,
- meaningless graphs,
- giant “AI magic” buttons.

---

# 39. PROJECT METRICS

Track these from early phases.

## Quality

- field top-1 accuracy,
- field top-3 recall,
- enum accuracy,
- relationship precision,
- relationship recall,
- unsafe wrong-map rate,
- confidence calibration.

## Automation

- auto-resolved mappings,
- review-required mappings,
- average human questions.

## Generation

- adapters generated,
- test pass rate,
- canonical validation success.

## Drift

- injected changes,
- detected changes,
- repair proposals,
- correct repair proposals,
- unsafe repair rate.

## System

- p50 latency,
- p95 latency,
- external calls,
- retries,
- failure rate,
- model tokens,
- estimated model cost.

## User outcome

- manual integration time,
- Crosswalk-assisted integration time,
- human corrections,
- user-reported usefulness.

---

# 40. DEFINITION OF DONE

Crosswalk is not done because the UI looks polished.

A strong finished version must:

1. Accept an unfamiliar API.
2. Parse its schema.
3. Explore/sample it.
4. Profile fields.
5. Propose mappings.
6. Explain evidence.
7. Admit uncertainty.
8. Let a human correct ambiguity.
9. Map enums.
10. Discover relationships.
11. Generate adapter code.
12. Generate tests.
13. Run adapter tests.
14. Produce valid canonical objects.
15. Benchmark on synthetic APIs.
16. Measure mapping quality.
17. Detect schema drift.
18. Generate candidate repairs.
19. Regression-test repairs.
20. Require human approval.
21. Run in cloud infrastructure.
22. Expose observability.
23. Survive common API failures.
24. Be tested by at least one external developer/team.
25. Document measured outcomes honestly.

---

# 41. RESUME-BULLET TARGET

Do not publish this until metrics are real.

Target shape:

> Built an autonomous enterprise integration system that inferred external API schemas, generated typed adapters, and regression-tested schema-drift repairs across **N endpoints / M payloads**, achieving **X% measured mapping accuracy** and reducing benchmark integration time from **A to B**.

The Planner AI should help the project earn a bullet like this, not fabricate it.

---

# 42. TASK FORMAT REQUIRED FROM THE PLANNER AI

Every task the Planner creates must use:

```markdown
## Task: <name>

### User problem
What real pain does this solve?

### Goal
What should exist after this task?

### Inputs
What comes in?

### Outputs
What comes out?

### Files likely touched
...

### Database changes
...

### API contract
...

### Algorithm / behavior
...

### Edge cases
...

### Failure cases
...

### Security considerations
...

### Tests
#### Unit
- ...

#### Integration
- ...

#### Contract
- ...

#### Eval
- ...

### Metrics affected
...

### Definition of done
- [ ] ...
```

---

# 43. BEFORE EVERY NEW FEATURE, THE PLANNER MUST ANSWER

1. Who uses this?
2. When do they use it?
3. What exact pain does it solve?
4. Where does the input data come from?
5. What is the output?
6. Can deterministic code solve this better?
7. Why is AI needed?
8. How will we evaluate it?
9. What can fail?
10. What security risk exists?
11. What test proves correctness?
12. How does this help FDE or SWE skill development?

If these answers are weak, redesign before coding.

---

# 44. RECOMMENDED BUILD ORDER

```text
Phase 0  Product definition
Phase 1  Canonical model + mock APIs
Phase 2  OpenAPI discovery
Phase 3  Value profiling
Phase 4  Baseline mapping
Phase 5  Human review
Phase 6  Enum mapping
Phase 7  Relationship discovery
Phase 8  Integration agent
Phase 9  Adapter generation
Phase 10 Test generation
------------------------------
MVP COMPLETE
------------------------------
Phase 11 Synthetic API generator
Phase 12 Evaluation harness
Phase 13 Drift detection
Phase 14 Repair proposals
Phase 15 Production runtime
Phase 16 Database hardening
Phase 17 Background jobs
Phase 18 Security
Phase 19 Cloud deployment
Phase 20 Observability
Phase 21 Real users
Phase 22 FDE playbook
Phase 23 Multimodal docs
Phase 24 Final polish
```

---

# 45. FINAL PLANNER RULE

**Simple outside. Deep inside.**

A recruiter should understand Crosswalk in 30 seconds.

A strong engineer should be able to spend a long interview discussing:

- schema inference,
- API exploration,
- mapping algorithms,
- statistical profiling,
- model evaluation,
- agent tools,
- confidence calibration,
- generated code,
- contract testing,
- database design,
- background jobs,
- security,
- drift,
- deployment,
- observability,
- customer feedback,
- failure handling.

The Planner AI must optimize for **real engineering ability**, not recruiter bait.
