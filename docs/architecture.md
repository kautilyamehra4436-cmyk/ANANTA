# ANANTA Architecture — executable foundation v0.2

## Source alignment
This foundation follows the supplied ANANTA Parts 1–3: eight named modules, central controller, evidence grades A–E, staged workflow, human approval for sensitive external actions, audit trail, and no unsupported claim of subjective consciousness.

## Runtime flow
`TaskRequest → VAK → MANAS → BUDDHI → PRAMANA → RITA → SAKSHI → Controller result`
AHAMKARA supplies identity/capability boundaries. YANTRA separately authorizes tool actions. This is a deterministic control skeleton; no LLM is integrated.

## Module contracts
- VAK validates non-empty input and carries language metadata; it does not translate.
- MANAS records the active objective and READY state; persistent memory is not implemented.
- BUDDHI emits a transparent fixed plan; it does not perform general reasoning.
- PRAMANA records attached evidence grade. An attached source is not automatically proof.
- RITA detects unknown dependencies and dependency cycles.
- SAKSHI flags claims with no attached evidence.
- AHAMKARA reports system identity and declared capability boundaries.
- YANTRA uses a deny-by-default allowlist and explicit approval gates.

## Deliberate limitations
No trained model, browser/search crawler, durable database, vector store, payment execution, robotics, background scheduler, or consciousness measurement is included. The audit log is in-memory in this first core and is lost when the process exits.

## Next engineering gates
1. Add persistent SQLite audit/event storage with schema migrations and integrity tests.
2. Add calibrated evaluation datasets and baseline-vs-module ablation tests.
3. Add a model adapter behind a strict interface; keep PRAMANA/SAKSHI independent of model output.
4. Add retrieval/search adapters with source snapshots and timestamps.
5. Add YANTRA capability tokens, scoped permissions, idempotency, rollback strategy, and emergency stop.
6. Add long-horizon task persistence only after privacy and retention policy is defined.
