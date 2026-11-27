# ANANTA — Modular AI Control and Evidence Framework

**स्थिति:** executable software foundation v0.4.0  
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

## v0.4.0 capability enablement
- Added a sandboxed executor for bounded arithmetic expressions and local Markdown report creation.
- Arithmetic uses a restricted Python AST interpreter; it does not call eval/exec, import modules, access files, or invoke a shell.
- Local reports are written only under the explicitly configured workspace's reports directory.
- Controller execution outcomes are recorded in the audit log.
- Unknown actions remain denied. The read_file action is not yet executable.

## Run
Python 3.11+:
```bash
python -m pip install -e ".[dev]"
pytest -q
python -m ananta
```

Runtime dependencies are standard-library-only; pytest is a development dependency. To enable durable audit storage and local report writing:
```python
from ananta import AnantaController, ToolAction
engine = AnantaController(
    audit_db_path="ananta-audit.sqlite3",
    workspace_dir="./ananta-workspace",
)
result = engine.execute_action(
    ToolAction("safe_calculation", {"expression": "(12 + 8) * 3"})
)
print(result)
engine.close()
```
For a report, call `execute_action(ToolAction("local_report", {"title": "Daily Status", "content": "..." }))`. Reports are stored under `workspace_dir/reports/`. Without a workspace, report creation fails closed. Without an audit path, audit records are ephemeral.

## Safety invariants and limitations
1. No evidence attached means a claim remains unverified.
2. An attached source is not automatically authentic and does not prove that it entails the claim.
3. Internal confidence is not a calibrated probability.
4. **Only two adapters execute:** bounded arithmetic and workspace-confined local reports. No shell, arbitrary Python, network, browser, payment, account, or system command execution is available.
5. Unknown actions and unknown payload fields are denied. `read_file` is authorized by policy in limited cases but has no execution adapter yet.
6. High-impact actions and file reads require an approval flag. **The current boolean is a policy placeholder, not cryptographic owner authentication or a secure approval token. Do not connect it directly to real money, accounts, legal filings, or production systems.**
7. Emergency stop is a local controller control; `owner_confirmed` is a caller-supplied confirmation flag, not identity verification.
8. The SQLite hash chain detects accidental or direct row tampering, but a privileged attacker able to rewrite the entire database and recompute hashes can defeat it. External anchoring/signing and access controls remain future work.
9. No trained LLM, autonomous web researcher, payment processor, durable task scheduler, robotics controller, or consciousness measurement is included.

## Roadmap gates
Next: authenticated owner identity and scoped expiring approval grants; SQLite migrations and concurrency tests; evidence provenance and source verification; sandboxed read-only file access; persistent task scheduler and privacy-scoped memory; approved model adapters and web research; reproducible research and separate functional self-observation vs experiential-consciousness research tracks.

See [Architecture](docs/architecture.md) and [Security](SECURITY.md).
