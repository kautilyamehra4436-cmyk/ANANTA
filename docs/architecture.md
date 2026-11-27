# ANANTA Architecture — executable foundation v0.3.0

## Source alignment
This foundation preserves the eight named modules, central controller, evidence grades A–E, staged workflow, deny-by-default action policy, and no unsupported claim of subjective consciousness.

## Runtime flow
`TaskRequest → VAK → MANAS → BUDDHI → PRAMANA → RITA → SAKSHI → Controller result`
AHAMKARA supplies identity/capability boundaries. YANTRA separately authorizes allowlisted actions. This remains a deterministic control skeleton; no LLM is integrated.

## Module contracts
- VAK validates the request object, non-empty text, maximum length, task identifier and language metadata; it does not translate.
- MANAS validates the parsed task shape and creates an in-memory READY working-state.
- BUDDHI emits a transparent fixed plan; it does not perform general reasoning.
- PRAMANA records attached evidence grade. An attached source is not automatically authentic or proof of claim entailment.
- RITA detects malformed dependency graphs, unknown dependencies and cycles using iterative traversal; it can produce a topological order.
- SAKSHI flags claims with no attached evidence; it is not an independent truth detector.
- AHAMKARA reports system identity and declared capability boundaries.
- YANTRA checks an allowlist, action-specific payload keys, relative file paths, approval flags and emergency stop. It does not execute actions.

## Audit
The controller supports ephemeral in-memory audit by default, or an optional SQLite ledger when `audit_db_path` is provided. SQLite events include UTC timestamp, unique event ID, canonical JSON details, previous hash and SHA-256 event hash. `verify_audit()` checks the chain. The chain is tamper-evident, not tamper-proof against an attacker who can rewrite the entire database and recompute hashes. SQLite schema migration, external anchoring, encryption and robust multi-process concurrency remain future work.

## Owner control and safety boundary
The current `human_approved` and `owner_confirmed` flags are placeholders supplied by the caller. They are not authenticated identity, scoped expiring tokens or non-replayable grants. They must be replaced by a trusted authentication/approval adapter before any production integration. No money movement, account deletion, legal filing, medical action or physical actuation is enabled.

## Deliberate limitations
No trained model, browser/search crawler, vector store, payment execution, robotics, background scheduler, persistent task memory, or consciousness measurement is included. Functional self-observation and experiential-consciousness research are separate future research tracks; neither is implemented or proven by this core.

## Next engineering gates
1. Authenticated owner identity and scoped, expiring, replay-resistant approval grants.
2. SQLite migrations, access control, backups, retention, and concurrent-writer tests.
3. Evidence provenance, snapshots, claim-to-source entailment review, contradiction handling and independent grading.
4. Persistent task scheduler and privacy-scoped memory.
5. Sandboxed tool adapters with idempotency, rollback and emergency-stop integration.
6. Reproducible research runner; separate functional self-observation and experiential-consciousness hypotheses, experiments and evidence ledgers.
