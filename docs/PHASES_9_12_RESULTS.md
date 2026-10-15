# Phases 9–12 results

The next four phases establish a deterministic MVP boundary:

- **Phase 9:** adapter specifications and credential-free transform source generation.
- **Phase 10:** pytest contract-test source generation for required canonical keys.
- **Phase 11:** seeded synthetic claim APIs with stable schemas and records.
- **Phase 12:** explicit answer-key evaluation with total, correct, unresolved, and accuracy fields.

The generators emit source only from typed inputs. They do not load credentials, perform network requests, invoke shells, or infer hidden ground truth. The evaluation harness accepts an explicit answer key so benchmark correctness remains isolated and auditable.
