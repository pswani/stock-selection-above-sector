# Roadmap

## Current phase
Milestone 5 is complete and Milestone 6 is now in progress with a narrow Growth slice added; true multi-pillar ranking is still deferred.

## Immediate milestones
1. Continue Milestone 6 by implementing the next narrowest pillar after Growth (Q, V, R, or S) on top of the completed normalization and partial-assembly contracts.
2. Implement the remaining pillars incrementally after that.
3. Wire ranking confidence/missing-data disclosure into result assembly.
4. Keep validation/backtest and explainability layers explicit about scaffold status until real behavior is implemented.
5. Address the repo-wide Ruff UP042 baseline when it is brought into scope.

## Cross-cutting readiness
- The re-uploaded framework PDF is now stored at `requirements/framework-primary-source.pdf` and should be treated as the more specific requirements source when it can be inspected reliably.
- Fresh-server environment initialization is standardized via `scripts/bootstrap.sh` and `scripts/validate-env.sh`.
- Environment scripts now check complete runtime/developer dependency availability before milestone work proceeds.
- `validate-env.sh` is self-contained (uv check + frozen sync) for newly provisioned servers.
- Local validation on 2026-03-16 confirmed the bootstrap/validation scripts run successfully; `uv run pytest -q` and `uv run pyright` pass locally.
- Current readiness blocker is 2 pre-existing repo-wide Ruff UP042 findings in `src/stock_selection/factors/registry.py`; targeted Ruff for changed provider/universe files passes cleanly.
- The latest review batch is complete: latest-only provider timing behavior is now explicit in the provider contract and FMP adapter.
- Milestone 4 is complete: normalization now covers peer-group primitives plus typed normalized-factor outputs and deterministic DataFrame projections with focused tests.
- Milestone 5 now has a narrow RP path from six-month return inputs to `PillarScoreCard` outputs with explicit diagnostics and coverage.
- The highest-value review batch is complete: RP now also plugs into the scoring abstraction through `PillarEngine`.
- The next RP consumer batch is also complete: reporting and CLI can now export actual RP score cards from the implemented path.
- The latest hardening batch is complete for current scope: config loading now validates profile names and pillar-weight shape more strictly, and reporting exports use deterministic dynamic column ordering with explicit empty schemas.
- The latest hardening batch is complete for current scope: config/schema validation now also rejects blank penalty rule names, rejects negative penalty rule weights, and reports invalid YAML or non-mapping roots more explicitly.
- The next broader RP assembly step is now complete: RP score cards can be grouped into deterministic per-ticker partial assemblies with explicit `insufficient_pillars` behavior and reporting projections, without starting other pillars or inventing final rankings.
- Milestone 5 is now complete: RP also has a ranking-adjacent preview consumer through `rank_relative_performance_assemblies(...)`, `relative_performance_preview_ranks_to_frame(...)`, `write_relative_performance_preview_csv(...)`, and `export-sample-relative-performance-preview`.
- The latest review batch is complete: provider security listings no longer invent sector data, and investability gating now distinguishes peer classification from exchange-only metadata.
- The latest audit batch is now complete: the misleading sample ranking export is replaced by an explicit public `export-demo-ranking` command, the old name remains only as a hidden deprecated alias, and RP CLI exports now declare themselves pipeline-backed while preview output remains explicit about not being final multi-pillar ranking.
- Milestone 6 has started with a deterministic Growth pillar slice built from `FundamentalSnapshot.revenue_growth_yoy`, plus focused assembly coverage showing `G` can coexist with `RP` without claiming a final multi-pillar ranking.
- Validation and explainability scaffolds now state their current limits explicitly in repo docs and module docstrings so they are less likely to be mistaken for production-ready backtesting or explainability layers.
- The top open review-driven gap remains broader framework incompleteness beyond the `RP` and `G` slices, followed by scaffolded validation/explainability depth and the repo-wide Ruff baseline.

## Working rule
Every non-trivial Codex session should leave behind a resumable checkpoint.
