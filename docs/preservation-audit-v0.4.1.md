# ANANTA v0.4.1 preservation audit

Audit date: 2026-11-28

## Immutable reference points
- v0.4.0 baseline: ae8b4ea4c7abff872ce37bc4e122b5db4aa8b3b4
- v0.4.1 current main: 214d157656e3a04d99a529f8beb2c14da5e911f5
- Safety branch: safety/pre-preservation-audit-20261128

## Compare result
The v0.4.1 change set is one commit ahead of v0.4.0 and touches seven paths: README.md, docs/architecture.md, pyproject.toml, src/ananta/__main__.py, src/ananta/execution.py, src/ananta/modules.py, and adds tests/test_adversarial.py. No files were reported deleted or renamed.

## Function preservation findings
- src/ananta/execution.py: existing public/class methods __init__, _calculate_node, calculate, _write_report, execute remain. New _validate_number was added. The calculation path now validates numeric constants and unary-operation results; report writing now uses a unique temporary file and atomic replacement. These are behavioral changes, not complete function removal.
- src/ananta/modules.py: RITA, VAK, MANAS, BUDDHI, AHAMKARA, PRAMANA, SAKSHI, and YANTRA remain. All prior method names remain: check_dependencies, topological_order, parse, focus, plan, boundaries, assess, has_unsupported_claims, review, authorize. RITA validation and topological ordering were changed; heapq-based ordering was introduced. AHAMKARA version identity changed from 0.4.0 to 0.4.1.
- src/ananta/controller.py and src/ananta/models.py are byte-for-byte unchanged between the two compared commits.
- SECURITY.md is byte-for-byte unchanged.
- __main__.py, README.md, docs/architecture.md, and pyproject.toml have small version/smoke-test/documentation changes.

## Restoration policy
This branch archives the exact v0.4.0 versions of execution.py and modules.py without replacing current source files. Git history remains the authoritative source for all other historical versions. No old source file is deleted or overwritten by this preservation branch.

## Verification boundary
This is a source-preservation/audit record, not a new test run. Previously reported CI result: 119 tests passed on each of Python 3.11, 3.12, and 3.13. Those were GitHub-hosted Linux runs, not Android-device tests. No Android test is claimed here.

## Next checks
1. Compare v0.3.0 and v0.4.0 source to identify any earlier intentional or accidental removals.
2. Run the full regression suite against both the current source and archived v0.4.0 snapshot.
3. Add tests for report-directory symlinks, numeric literal bounds, invalid dependency members, duplicate edges, and large dependency graphs.
4. Keep any compatibility restoration additive and isolated; merge only after CI passes.
