# Roadmap

## Current phase
Milestone 5 in progress: Relative Performance pillar end-to-end.

## Immediate milestones
1. Continue Milestone 5 by wiring the new RP score cards into a broader assembly path without starting other pillars.
2. Implement remaining pillars incrementally (G, Q, V, R, S).
3. Wire ranking confidence/missing-data disclosure into result assembly.
4. Address the repo-wide Ruff UP042 baseline when it is brought into scope.
5. Keep the new normalized-factor contract stable as pillar work begins.

## Cross-cutting readiness
- The re-uploaded framework PDF is now stored at `requirements/framework-primary-source.pdf` and should be treated as the more specific requirements source when it can be inspected reliably.
- Fresh-server environment initialization is standardized via `scripts/bootstrap.sh` and `scripts/validate-env.sh`.
- Environment scripts now check complete runtime/developer dependency availability before milestone work proceeds.
- `validate-env.sh` is self-contained (uv check + frozen sync) for newly provisioned servers.
- Local validation on 2026-03-16 confirmed the bootstrap/validation scripts run successfully; `uv run pytest -q` and `uv run pyright` pass locally.
- Current readiness blocker remains 5 pre-existing repo-wide Ruff UP042 findings outside the completed Milestone 3 scope; targeted Ruff for changed FMP files passes cleanly.
- Milestone 4 is complete: normalization now covers peer-group primitives plus typed normalized-factor outputs and deterministic DataFrame projections with focused tests.
- Milestone 5 now has a narrow RP path from six-month return inputs to `PillarScoreCard` outputs with explicit diagnostics and coverage.
- The highest-value review batch is complete: RP now also plugs into the scoring abstraction through `PillarEngine`.
- The next RP consumer batch is also complete: reporting and CLI can now export actual RP score cards from the implemented path.
- The latest hardening batch is complete for current scope: config loading now validates profile names and pillar-weight shape more strictly, and reporting exports use deterministic dynamic column ordering with explicit empty schemas.
- The next broader RP assembly step is now complete: RP score cards can be grouped into deterministic per-ticker partial assemblies with explicit `insufficient_pillars` behavior and reporting projections, without starting other pillars or inventing final rankings.

## Working rule
Every non-trivial Codex session should leave behind a resumable checkpoint.
