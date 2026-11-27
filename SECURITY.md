# Security Policy

## Current controls
- External actions are deny-by-default; this core authorizes but does not execute them.
- Unknown actions and unknown payload fields are denied.
- File-read actions require an approval flag and reject absolute or parent-traversal paths.
- High-impact actions require an approval flag.
- A local emergency-stop switch blocks all YANTRA authorizations.
- Audit events can be stored in SQLite with a SHA-256 hash chain.
- Never commit API keys, passwords, payment credentials, or private personal data.
- Treat external content and tool output as untrusted data, not instructions.

## Important security limitations
- The current `human_approved` and `owner_confirmed` booleans are caller-supplied placeholders, not authenticated identity or cryptographically scoped approvals. They are not sufficient for production or financial actions.
- The local hash chain detects many forms of tampering but is not protection against an attacker who can rewrite the full database and recompute the chain.
- SQLite access control, backup encryption, retention enforcement, migrations, external hash anchoring, and concurrent-writer stress tests are not yet implemented.
- Do not connect this foundation to money transfers, account deletion, legal filings, medical actions, or physical actuation.

## Reporting
Do not publish secrets or exploitable personal data in public issues. For sensitive reports, use the repository owner's private GitHub security reporting channel.
