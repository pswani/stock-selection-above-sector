# Roadmap

## Current phase
Milestone 6 is now complete for the initial six-pillar scoring/ranking batch, and the audit backlog is fully closed. The next review-driven work shifts to validation depth and explainability expansion.

## Immediate milestones
1. Deepen validation realism beyond the current deterministic turnover/cost harness.
2. Expand explainability beyond summary cards into richer ranking diagnostics when needed.

## Cross-cutting readiness
- The re-uploaded framework PDF is now stored at `requirements/framework-primary-source.pdf` and should be treated as the more specific requirements source when it can be inspected reliably.
- Fresh-server environment initialization is standardized via `scripts/bootstrap.sh` and `scripts/validate-env.sh`.
- Environment scripts now check complete runtime/developer dependency availability before milestone work proceeds.
- `validate-env.sh` is self-contained (uv check + frozen sync) for newly provisioned servers.
- Local validation on 2026-03-16 confirmed the bootstrap/validation scripts run successfully; `uv run pytest -q` and `uv run pyright` pass locally.
- Repo-wide lint baseline is now clean: `uv run ruff check .` passes locally.
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
- Milestone 6 now covers all six pillars and a deterministic composite ranking path, with pipeline-backed sample exports for final ranking, explanation cards, and validation results.
- The validation layer now includes a deterministic top-k harness with turnover, transaction costs, benchmark-relative excess returns, and explicit assumptions/limitations.
- The validation harness now also keeps partial cash allocation explicit when fewer than `top_k` names are available, and period outputs expose invested weight, cash weight, and buy/sell turnover.
- The validation harness now also validates unique period dates, ranking-result date alignment, and non-blank benchmark names, and period outputs expose benchmark-relative gap in bps for easier reporting.
- The explainability layer now includes deterministic explanation-card generation derived from ranking outputs, plus structured explanation/reporting details for top pillars, weakest pillars, penalties, and missing coverage.
- Reporting now has deterministic export helpers for explanation cards and validation periods in addition to the earlier ranking and assembly exports.
- The top open review-driven gap is now deeper validation realism, followed by richer explainability diagnostics when needed.

## Working rule
Every non-trivial Codex session should leave behind a resumable checkpoint.
