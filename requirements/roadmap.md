# Roadmap

## Current phase
Milestone 3 in progress: FMP adapter now covers core providers plus initial corporate-actions and ownership/short-interest retrieval with explicit unsupported fallbacks.

## Immediate milestones
1. Harden Milestone 3 provider coverage for corporate actions and ownership/short-interest (broader endpoint coverage, field mapping robustness, and endpoint-availability diagnostics).
2. Implement sector-relative normalization engine with explicit missing-data behavior.
3. Implement first end-to-end pillar: Relative Performance.
4. Implement remaining pillars incrementally (G, Q, V, R, S).
5. Wire ranking confidence/missing-data disclosure into result assembly.

## Cross-cutting readiness
- Fresh-server environment initialization is standardized via `scripts/bootstrap.sh` and `scripts/validate-env.sh`.
- Environment scripts now check complete runtime/developer dependency availability before milestone work proceeds.
- `validate-env.sh` is self-contained (uv check + frozen sync) for newly provisioned servers.

## Working rule
Every non-trivial Codex session should leave behind a resumable checkpoint.
