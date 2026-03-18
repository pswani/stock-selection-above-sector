# Audit Findings

## Summary
- High: 0 open, 1 fixed
- Medium: 4
- Low: 1

## Issues

### AUDIT-001 — Provider timing contract is under-specified for point-in-time use
- Severity: High
- Category: provider integrity / validation safety
- Files affected: `src/stock_selection/data/providers.py`, `src/stock_selection/data/fmp.py`, `docs/validation-spec.md`, `tests/test_fmp_provider.py`
- Description: Several provider methods accept `as_of`, but at least `list_securities(...)` and `get_peer_groups(...)` use latest-state endpoints. The code comments acknowledge this in one implementation, but the provider contract does not clearly distinguish latest-only methods from point-in-time-safe methods.
- Why it matters: This creates a look-ahead risk if these methods are reused in validation or backtesting under an implied point-in-time contract.
- Recommended fix: Make latest-only behavior explicit at the provider-contract boundary and in the FMP adapter, then add focused tests that guard against accidental point-in-time claims.
- Test expectation: Add contract-level tests or assertions confirming latest-only methods remain explicitly labeled and do not imply point-in-time fidelity.
- Dependencies: None.
- Status: Verified complete on 2026-03-17. The provider interfaces now document latest-only behavior explicitly, the FMP adapter documents `list_securities(...)` and `get_peer_groups(...)` as latest-state only and not point-in-time safe, and focused tests pin that wording at both the provider-contract and adapter levels.

### AUDIT-002 — CLI final ranking export still bypasses the implemented scoring pipeline
- Severity: Medium
- Category: scoring / reporting / maintainability
- Files affected: `src/stock_selection/cli/main.py`, `src/stock_selection/scoring/composite.py`, `tests/test_cli.py`
- Description: `export_sample_ranking` still builds hardcoded sample `RankingResult` rows rather than consuming the implemented normalization, pillar, or partial-assembly path. This sits alongside the newer RP preview exports, which do exercise real pipeline code.
- Why it matters: The CLI surface mixes genuine pipeline-backed exports with hand-built sample ranking output, which weakens confidence in the ranking path and makes the interface harder to reason about.
- Recommended fix: Keep the sample command clearly scoped as demo-only or replace it with the next smallest pipeline-backed ranking/export consumer when multi-pillar semantics exist.
- Test expectation: Add focused CLI tests that make the command contract explicit, especially if the command is renamed, narrowed, or replaced.
- Dependencies: Either a docs-only clarification or later multi-pillar ranking work.
- Status: Verified complete on 2026-03-17. The public hardcoded ranking export is now explicitly `export-demo-ranking`, `export-sample-ranking` remains only as a hidden deprecated alias, and RP CLI exports now state when they are pipeline-backed preview versus non-preview paths.

### AUDIT-003 — Framework implementation remains partial beyond the RP slice
- Severity: Medium
- Category: missing components / framework scope
- Files affected: `src/stock_selection/scoring/relative_performance.py`, `src/stock_selection/scoring/composite.py`, `src/stock_selection/cli/main.py`, `tests/`
- Description: Milestones 4 and 5 are implemented, but only Relative Performance exists as an end-to-end pillar path. Growth, Quality, Valuation, Risk, and Sentiment are still unimplemented, and the repo does not yet provide a true multi-pillar ranking path.
- Why it matters: The repository now has a valid thin slice, but it is still short of the intended stock-selection framework described in the roadmap and scoring docs.
- Recommended fix: Continue milestone work incrementally, starting with the narrowest Growth pillar path while preserving the current normalization and partial-assembly contracts.
- Test expectation: Each new pillar should add focused factor, normalization-integration, scoring, and partial-assembly tests.
- Dependencies: Current Milestone 4 and Milestone 5 contracts.
- Status: Partially remediated on 2026-03-17. The repo now includes a narrow deterministic Growth pillar slice built from `revenue_growth_yoy`, plus focused tests and mixed `RP` + `G` partial-assembly coverage. Quality, Valuation, Risk, Sentiment, and any true multi-pillar ranking path remain open.

### AUDIT-004 — Explainability and backtest layers are still scaffolds
- Severity: Medium
- Category: validation / backtesting / explainability
- Files affected: `src/stock_selection/backtest/snapshots.py`, `src/stock_selection/explainability/models.py`, `docs/validation-spec.md`
- Description: Backtesting currently stops at writing ranking snapshots, and explainability is only a basic model shell. The code does not yet enforce or model turnover, transaction costs, benchmark alignment, or timing safety.
- Why it matters: The docs emphasize anti-bias and validation safety, so these layers should remain explicitly incomplete rather than being mistaken for production-ready validation support.
- Recommended fix: Keep these deferred, but preserve them as explicit later milestones with anti-bias acceptance criteria before any validation claims are made.
- Test expectation: Add snapshot and validation tests only when these layers gain real behavior.
- Dependencies: Broader scoring and ranking pipeline.
- Status: Partially remediated on 2026-03-17. The scaffold limits are now explicit in repo docs and module docstrings, but the layers remain intentionally thin until later milestones add real validation and explainability behavior.

### AUDIT-005 — RP missing-data scoring policy is explicit but still provisional
- Severity: Medium
- Category: missing-data handling / scoring semantics
- Files affected: `src/stock_selection/scoring/relative_performance.py`, `tests/test_relative_performance.py`, `docs/scoring-spec.md`
- Description: When RP normalization cannot produce a percentile, the score falls back to `0.0` while diagnostics and coverage remain explicit. This is deterministic and documented, but it is still a provisional policy rather than a framework-wide missing-data rule.
- Why it matters: As more pillars are added, this policy may interact awkwardly with minimum-pillar rules, confidence semantics, and future composite ranking behavior.
- Recommended fix: Revisit the fallback only when broader ranking coverage policy is formalized, so missing-data semantics stay coherent across pillars.
- Test expectation: When broader ranking semantics arrive, add tests that cover partial coverage, minimum-pillar thresholds, and missing-factor behavior across multiple pillars.
- Dependencies: Later multi-pillar ranking work.

### AUDIT-006 — Repo-wide lint baseline is still not clean
- Severity: Low
- Category: lint / maintainability
- Files affected: `src/stock_selection/factors/registry.py`
- Description: `uv run ruff check .` still fails on two `UP042` findings because `PillarName` and `MissingDataPolicy` inherit from `str, Enum` instead of `StrEnum`.
- Why it matters: This is low risk, but it keeps the repository below a clean-lint baseline and obscures new lint signal during later review work.
- Recommended fix: Convert the remaining registry enums to `StrEnum` in a small, behavior-preserving lint batch.
- Test expectation: Re-run `uv run ruff check .` and verify that the remaining baseline is clean.
- Dependencies: None.
