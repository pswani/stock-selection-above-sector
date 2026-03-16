# Roadmap

## Current phase
Milestone 3 in progress: provider contracts expansion started with Financial Modeling Prep (FMP) primary provider adapter.

## Immediate milestones
1. Complete Milestone 3 provider contract expansion (corporate actions and ownership/short-interest data retrieval where available; explicit unsupported-capability handling already added, including lint-compliant error naming).
2. Implement sector-relative normalization engine with explicit missing-data behavior.
3. Implement first end-to-end pillar: Relative Performance.
4. Implement remaining pillars incrementally (G, Q, V, R, S).
5. Wire ranking confidence/missing-data disclosure into result assembly.

## Cross-cutting readiness
- Fresh-server environment initialization is standardized via `scripts/bootstrap.sh` and `scripts/validate-env.sh`.
- Environment scripts now check complete runtime/developer dependency availability before milestone work proceeds.
- `validate-env.sh` is self-contained (uv check + frozen sync) for newly provisioned servers.
- Local validation on 2026-03-16 confirmed the bootstrap/validation scripts now run successfully; current readiness blockers are repo-wide Ruff and pyright failures rather than environment connectivity.

## Working rule
Every non-trivial Codex session should leave behind a resumable checkpoint.
