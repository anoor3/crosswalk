# Phase 6 implementation plan

## Task: Safe enum mapping

### User problem
External APIs encode the same lifecycle values differently: `OPEN`, `OPN`,
or numeric codes such as `1`. A mapper must translate known values without
turning an unseen production value into a silently incorrect canonical status.

### Goal
Provide a deterministic enum-mapping domain package that records evidence,
alternatives, unknown values, and safe translation failures.

### Inputs and outputs

The mapper accepts declared external values, canonical values, optional observed
values, descriptions, and explicit mappings. It returns one candidate per
declared value plus an `unseen_values` list for observed values outside the
declared vocabulary.

### Rules

- Exact values and conservative status abbreviations can be high-confidence.
- Explicit caller mappings are marked confirmed and can translate numeric codes.
- Ambiguous description evidence remains conflicting or review-required.
- Numeric codes without evidence remain unknown.
- Unseen runtime values raise `UnknownEnumValueError`.
- Known review-required or conflicting values raise `UnapprovedEnumMappingError`.

### Definition of done

The package has typed models, deterministic mapping and translation functions,
unit tests, fixture integration tests for all three APIs, documentation, and
full repository quality gates. No hidden ground truth is imported by the enum
package or integration tests.
