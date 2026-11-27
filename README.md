# ANANTA — Modular AI Control and Evidence Framework

**स्थिति:** executable software foundation v0.3.0  
**PRIMORDIAL** = शोध/डिजाइन दर्शन; **ANANTA** = उस पर आधारित AI system। यह deterministic control framework है; subjective consciousness का दावा नहीं करता।

## आठ मूल modules
- **RITA:** dependency validation और topological ordering
- **VAK:** request type, length और language metadata validation
- **MANAS:** task focus और working-state
- **BUDDHI:** structured task plan
- **AHAMKARA:** identity और capability boundaries
- **SAKSHI:** unsupported-claim review
- **PRAMANA:** evidence attachment ledger; source attachment को proof नहीं मानता
- **YANTRA:** allowlisted action authorization, payload checks और emergency-stop enforcement

## v0.3.0 hardening
- Validated immutable request/claim/evidence contracts and bounded JSON action payloads.
- Iterative dependency-cycle detection; avoids recursive DFS depth failure.
- Optional SQLite audit ledger with UTC timestamps, unique event IDs and SHA-256 hash chaining.
- Defensive copies from in-memory audit reads.
- YANTRA action-specific payload validation and workspace-relative file path checks.
- Owner-confirmed emergency-stop switch in the controller.
- Expanded regression tests for malformed data, path traversal, dependency graphs, audit persistence and tamper detection.

## Run
Python 3.11+:
```bash
python -m pip install -e ".[dev]"
pytest -q
python -m ananta
```

Runtime dependencies are standard-library-only; pytest is a development dependency. To enable durable audit storage, instantiate `AnantaController(audit_db_path="ananta-audit.sqlite3")` and call `close()` when finished. Without a path, audit records are ephemeral and disappear when the process exits.

## Safety invariants and limitations
1. No evidence attached means a claim remains unverified.
2. An attached source is not automatically authentic and does not prove that it entails the claim.
3. Internal confidence is not a calibrated probability.
4. External actions are not executed by this core; YANTRA only returns an authorization decision.
5. Unknown actions and unknown payload fields are denied.
6. High-impact actions and file reads require an approval flag. **The current boolean is a policy placeholder, not cryptographic owner authentication or a secure approval token. Do not connect it directly to real money, accounts, legal filings, or production systems.**
7. Emergency stop is a local controller control; `owner_confirmed` is a caller-supplied confirmation flag, not identity verification.
8. The SQLite hash chain detects accidental or direct row tampering, but a privileged attacker able to rewrite the entire database and recompute hashes can defeat it. External anchoring/signing and access controls remain future work.
9. No trained LLM, autonomous web researcher, payment processor, durable task scheduler, robotics controller, or consciousness measurement is included.

## Roadmap gates
Next required gates: authenticated owner identity and scoped expiring approval grants; SQLite migrations, file permissions and concurrent-writer tests; source provenance and independent evidence review; sandboxed execution adapters; privacy/retention policy; reproducible research and separate functional self-observation vs experiential-consciousness research tracks.

See [Architecture](docs/architecture.md) and [Security](SECURITY.md).
