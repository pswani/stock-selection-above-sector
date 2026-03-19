# Execution Plans

Use this file for larger multi-session efforts that benefit from a stable plan.

## How to use
- Create a new dated section for each major initiative.
- Keep the plan implementation-oriented and repo-specific.
- Update status after every meaningful Codex session.
- Link the active plan from `requirements/session-handoff.md`.

## Plan Template

### YYYY-MM-DD — <initiative name>
Status: proposed | in_progress | blocked | complete
Owner: Codex
Related files:
- path/to/file.py
- docs/example.md

Objective:
- What the milestone should accomplish.

Design constraints:
- No invented financial data.
- Deterministic calculations first, LLMs only for explanation and extraction.
- Keep provider interfaces separate from scoring logic.

Work breakdown:
1. Step one
2. Step two
3. Step three

Validation:
- tests to run
- assumptions to verify

Risks / open questions:
- Item

Resume prompt:
- Exact copy-paste prompt to continue this plan.

---

### 2026-03-16 — Full stock-selection framework implementation
Status: in_progress
Owner: Codex
Related files:
- `src/stock_selection/models.py`
- `src/stock_selection/factors/`
- `src/stock_selection/universe/`
- `src/stock_selection/data/providers.py`
- `src/stock_selection/normalize/`
- `src/stock_selection/scoring/`
- `src/stock_selection/penalties/`
- `src/stock_selection/backtest/`
- `src/stock_selection/reporting.py`
- `src/stock_selection/cli/main.py`
- `tests/`
- `docs/architecture.md`
- `docs/scoring-spec.md`
- `docs/validation-spec.md`

Objective:
- Deliver the full deterministic, modular, testable framework for sector-relative stock selection in small resumable milestones.

Design constraints:
- No invented financial data or fake provider behavior.
- Deterministic and config-driven scoring and penalties.
- Explicit missing-data handling and confidence surfacing.
- Strong typed schemas and validation.
- Isolated provider abstractions from factor/scoring logic.

Milestones:
1. **Milestone 1 — Canonical factor schema + registry (completed)**
   - Scope:
     - Add canonical factor definitions and validated metadata schema.
     - Add deterministic registry for factor definitions with duplicate protection.
     - Add missing-data policy fields needed by later pillar implementations.
   - Acceptance criteria:
     - Factor definition model validates required metadata and direction.
     - Registry supports register/get/list deterministically.
     - Duplicate registration and unknown lookup failures are explicit.
   - Tests:
     - Unit tests for schema validation.
     - Unit tests for registry behaviors and deterministic ordering.
   - Dependencies: none.

2. **Milestone 2 — Investable universe + peer mapping foundations (completed)**
   - Scope: eligibility contract, classification-level peer mapping helpers, configurable exclusion rules.
   - Acceptance criteria: deterministic eligibility output and peer groups for sector/industry/sub-industry.
   - Tests: unit tests for filters and mapping edge cases.
   - Dependencies: Milestone 1.

3. **Milestone 3 — Provider contracts expansion (completed)**
   - Scope: extend provider interfaces for prices/returns/volume, corporate actions, fundamentals, estimates/revisions, ownership/short-interest (optional availability).
   - Acceptance criteria: typed provider interfaces and fixtures; unsupported datasets reported explicitly.
   - Tests: interface fixture tests + missing-data behavior tests.
   - Progress: FMP primary adapter now implements securities/prices/fundamentals/estimates/peer-groups plus supported corporate-actions and ownership/short-interest retrieval. Field coverage includes split ratio strings (`a:b`, `a/b`), percentage ownership/short-interest aliases, broader fundamentals/estimates aliases, and final safe non-`TTM` ratio fallbacks for already-supported canonical fields. Tests cover supported/missing/unsupported paths and alias fallback behavior. Full local validation passes for pytest and pyright; remaining blocker is 5 pre-existing repo-wide Ruff UP042 findings outside Milestone 3 scope.
   - Dependencies: Milestones 1-2.

4. **Milestone 4 — Sector-relative normalization engine (completed)**
   - Scope: peer-relative percentile/z-score normalization with robust missing-data handling.
   - Acceptance criteria: deterministic normalized outputs for fixed fixtures and peer groups.
   - Tests: unit tests covering tiny peer groups, ties, nulls, outliers.
   - Progress: added a DataFrame-based peer-group normalization engine in `src/stock_selection/normalize/peer.py` that computes winsorized values, percentile ranks, robust z-scores, peer-group size/coverage, and explicit row statuses for missing peer groups, missing values, and insufficient valid peers. Added `src/stock_selection/normalize/factors.py` as the downstream factor consumer: it accepts `FactorObservation` records, applies direction-aware normalization (`LOWER_IS_BETTER` values are sign-flipped into `oriented_value`), and returns typed `NormalizedFactorObservation` outputs plus deterministic DataFrame projections. Focused tests now cover ties, tiny groups, nulls, outliers, required-column validation, factor-output integration, and frame projection from typed outputs.
   - Dependencies: Milestones 1-3.

5. **Milestone 5 — Relative Performance (RP) pillar end-to-end (completed)**
   - Scope: first complete pillar from factor inputs to normalized pillar score.
   - Acceptance criteria: RP score card produced with diagnostics and coverage ratio.
   - Tests: unit tests + integration test through composite assembly.
   - Progress: added `src/stock_selection/scoring/relative_performance.py` with a narrow end-to-end RP path. `build_relative_performance_observations(...)` constructs deterministic `relative_strength_6m` factor observations from six-month return inputs and peer groups, `score_relative_performance(...)` converts normalized outputs into `PillarScoreCard` results with diagnostics and coverage, and `RelativePerformancePillarEngine` now plugs RP into the scoring abstraction. Reporting/CLI now have a deterministic consumer for RP score cards through `pillar_score_cards_to_frame(...)`, `write_pillar_score_cards_csv(...)`, and `export-sample-relative-performance`. The broader assembly seam is implemented via `assemble_pillar_score_cards(...)`, which groups available pillar score cards per ticker, preserves per-pillar coverage/diagnostics, and marks `insufficient_pillars` explicitly when `min_required_pillars` is not met. Reporting can project these partial assemblies through `pillar_score_assemblies_to_frame(...)` and `write_pillar_score_assemblies_csv(...)`. Milestone 5 now also includes a ranking-adjacent preview consumer through `rank_relative_performance_assemblies(...)`, `relative_performance_preview_ranks_to_frame(...)`, `write_relative_performance_preview_csv(...)`, and `export-sample-relative-performance-preview`. Focused tests cover happy-path scoring, explicit missing-data behavior, requested-ticker engine behavior, partial assembly behavior, preview ranking determinism, reporting, and CLI export.
   - Dependencies: Milestones 1-4.

6. **Milestone 6 — Remaining pillars (G, Q, V, R, S) incremental**
   - Scope: implement one pillar per sub-step with explicit formulas and missing-data behavior.
   - Acceptance criteria: all six pillars produce deterministic score cards with traces.
   - Tests: per-pillar unit tests and integration checks.
   - Progress: Milestone 6 is now complete for the initial six-pillar delivery. In addition to the earlier RP and Growth paths, the repo now includes deterministic `Q`, `V`, `R`, and `S` pillar engines plus `build_composite_rankings(...)` in `src/stock_selection/scoring/pipeline.py`, which scores all six pillars, assembles complete pillar sets, applies configured weights and penalties, and emits final ranking results. Focused tests cover each added pillar, the composite ranking pipeline, explanation-card generation, validation behavior, and pipeline-backed CLI/reporting exports.
   - Dependencies: Milestones 1-5.

7. **Milestone 7 — Rule-based penalties and regime sensitivity**
   - Scope: hype trap, value trap, momentum crash penalties, config-driven thresholds.
   - Acceptance criteria: penalty traces auditable and deterministic.
   - Tests: rule unit tests for fire/no-fire boundaries.
   - Dependencies: Milestones 1-6.

8. **Milestone 8 — Ranking outputs + explainability cards**
   - Scope: per-sector and global ranks, confidence scores, missing-data disclosure, explainability payloads.
   - Acceptance criteria: ranking artifacts include required fields and confidence behavior.
   - Tests: integration tests for ranking assembly and explainability output.
   - Progress: explanation cards now expose structured top/weakest pillar details, penalty-rule names, assembly status, and missing-pillar disclosure, and the reporting layer can export those cards deterministically.
   - Dependencies: Milestones 1-7.

9. **Milestone 9 — Validation/backtest harness**
    - Scope: monthly/quarterly rebalance, sector-neutral/global top-k, benchmark comparison, turnover/cost model, anti-bias guards, false-positive and regime tests.
    - Acceptance criteria: reproducible validation run from fixtures with documented assumptions/limits.
    - Tests: integration/snapshot tests for backtest outputs and guardrails.
    - Progress: the validation harness now preserves explicit residual cash when fewer than `top_k` names are available and surfaces invested weight, cash weight, and buy/sell turnover in period results instead of silently reweighting underfilled periods to 100% invested.
    - Progress: the harness now also validates unique period dates, ranking-result `as_of` alignment, and non-blank benchmark names, and the reporting layer can export deterministic validation-period diagnostics including benchmark-relative gap in bps.
    - Progress: the harness now also exposes next rebalance anchors and inferred holding-period days, and reporting/CLI surfaces can export validation summaries plus validation periods from the implemented pipeline-backed sample path.
    - Progress: benchmark metadata is now a first-class validation contract, period inputs must arrive in explicit increasing order rather than relying on implicit sorting, and validation outputs now include period index, fill ratio, and underfilled diagnostics for easier interpretation.
    - Progress: deterministic benchmark-family fixtures now support the sample validation flows, and validation outputs now expose period start/end anchors, benchmark outperformance counts, and cumulative benchmark-relative progression for easier end-to-end interpretation.
    - Dependencies: Milestones 1-8.

10. **Milestone 10 — CLI/reporting/export workflow hardening**
    - Scope: finalize CLI entry points for scoring, ranking, export, validation reports.
    - Acceptance criteria: documented CLI workflow runs end-to-end on sample fixtures.
    - Tests: CLI smoke tests + export contract tests.
    - Progress: CLI now includes pipeline-backed sample exports for explanation cards and validation reports in addition to the existing RP exports and explicit demo-only ranking command.
    - Progress: CLI now also includes a pipeline-backed analysis bundle export, and explanation/reporting outputs expose richer ranking coverage and benchmark metadata details without changing the established semantics of existing commands.
    - Progress: CLI now also includes a pipeline-backed benchmark-fixture export and a richer analysis-bundle manifest so the benchmark/reporting assumptions behind sample flows are inspectable outside the terminal.
    - Dependencies: Milestones 1-9.

Validation per milestone:
- `uv run pytest -q` (or targeted tests for changed modules)
- `uv run ruff check .`
- `uv run pyright`

Risks / open questions:
- Final factor formulas/threshold calibrations are still pending and must remain config-driven.
- FMP adapter is now the primary provider entry point; provider-contract expansion is complete, and the next delivery risk shifts to documenting and implementing deterministic peer-relative normalization behavior for small/incomplete groups.
- The normalized-factor contract is now typed; the next delivery risk is choosing the smallest RP pillar inputs/formulas that use it without prematurely generalizing for later pillars.
- Missing normalized percentiles now remain `None` at the pillar-score level, and composite assembly counts only non-`None` scores toward minimum-pillar coverage.
- Environment initialization reproducibility is addressed with bootstrap/validation scripts; keep these scripts aligned with `uv.lock`, `.python-version`, and the full runtime/dev dependency set as dependencies change, and keep `validate-env.sh` self-contained for fresh servers.

Resume prompt:
- Continue the active plan in `PLANS.md` at "2026-03-16 — Full stock-selection framework implementation", continue Milestone 5 only by wiring the RP score cards into the next smallest consumer or assembly path without starting other pillars, then update handoff/roadmap/decisions after running tests.

---

### 2026-03-16 — Repository Audit Plan
Status: in_progress
Owner: Codex
Related files:
- `src/stock_selection/scoring/composite.py`
- `src/stock_selection/scoring/relative_performance.py`
- `src/stock_selection/cli/main.py`
- `src/stock_selection/backtest/`
- `src/stock_selection/explainability/`
- `tests/`

Objective:
- Review the repository against the framework docs, fix the single highest-value batch, and leave a prioritized follow-up plan for remaining gaps.

Findings:
1. Severity `P1`: the initial RP pillar path produced `PillarScoreCard` outputs but was not wired into the existing scoring abstraction, leaving an architecture gap between pillar implementations and consumers.
   Recommended fix: make `PillarEngine` score cards the primary pillar output and let score maps derive from them.
   Status: fixed in this session.
2. Severity `P1`: the scoring pipeline still lacks the next minimal consumer for RP score cards, so the first pillar exists but is not yet assembled into a broader scoring flow.
   Recommended fix: add the smallest assembly or reporting consumer that consumes RP score cards without introducing other pillars.
   Status: fixed in changed scope via reporting/CLI export, explicit partial pillar assembly, and RP preview ranking consumer.
3. Severity `P2`: CLI/export remains sample-data oriented and does not exercise the live deterministic scoring path, which weakens end-to-end confidence.
   Recommended fix: add a narrow CLI/reporting entry point for deterministic RP outputs from fixtures.
   Status: fixed in changed scope for RP via `export-sample-relative-performance`.
4. Severity `P2`: explainability and backtest layers are still scaffolds, so framework fidelity to validation/backtesting goals remains partial.
   Recommended fix: keep these deferred until after pillar assembly, but explicitly preserve anti-bias requirements in later milestones.
5. Severity `P2`: missing-data semantics for pillar scores currently use a `0.0` fallback when RP normalization cannot produce a percentile; this is explicit but may need refinement when ranking coverage policy is formalized.
   Recommended fix: revisit only when coverage/min-required-pillar behavior is implemented so policy stays coherent.
   Status: fixed on 2026-03-18. Pillar scores now preserve missing normalized percentiles as `None`, and composite assemblies count only scored pillars toward availability and final-ranking eligibility.
6. Severity `P3`: repo-wide Ruff `UP042` baseline findings continue to obscure changed-scope lint signal.
   Recommended fix: address the baseline in a dedicated lint batch when brought into scope.
   Status: fixed on 2026-03-18. `PillarName` and `MissingDataPolicy` now inherit from `StrEnum`, preserving behavior while restoring a clean repo-wide Ruff baseline.
7. Severity `P2`: config validation was too permissive for the existing scoring contract, allowing invalid pillar-weight maps to survive until later scoring code.
   Recommended fix: validate required pillar coverage, non-negative weights, and positive total weight at config-load time with clearer errors.
   Status: fixed in this session.
8. Severity `P3`: reporting exports had under-specified empty/dynamic-column behavior, which weakened determinism for CSV contracts.
   Recommended fix: use stable base schemas and deterministic dynamic-column ordering.
   Status: fixed in this session.

Dependencies:
1. Completed normalization contract from Milestone 4.
2. Existing `PillarScoreCard` / composite interfaces in `src/stock_selection/scoring/composite.py`.
3. Existing RP factor name contract in `src/stock_selection/factors/registry.py`.

Acceptance criteria:
1. The highest-value batch closes a real architecture or correctness gap rather than adding new scaffolding alone.
2. The changed path remains deterministic and explicit about missing data.
3. Focused tests cover the changed RP/scoring integration path.
4. `uv run pyright` passes and changed-scope Ruff checks pass.
5. Remaining gaps are documented explicitly in handoff and roadmap files.

Latest progress:
1. Added `requirements/framework-primary-source.pdf` as the stored primary framework source for future sessions.
2. Hardened `src/stock_selection/config.py` so invalid scoring profiles fail earlier with clearer messages.
3. Hardened `src/stock_selection/reporting.py` so ranking and pillar exports keep deterministic dynamic columns and explicit empty schemas.
4. Added focused regression tests in `tests/test_config.py` and `tests/test_reporting.py`.
5. Added deterministic partial assembly for pillar score cards in `src/stock_selection/scoring/composite.py` plus reporting projections for that assembly.
6. Completed Milestone 5 by adding an RP-only preview ranking/export consumer on top of the partial assemblies.
7. Added another focused hardening pass for the config layer: penalty rule names/weights now validate earlier, YAML parse errors are path-aware, and non-mapping roots report their actual type.

---

### 2026-03-17 — Comprehensive Review Refresh
Status: in_progress
Owner: Codex
Related files:
- `src/stock_selection/models.py`
- `src/stock_selection/data/fmp.py`
- `src/stock_selection/data/providers.py`
- `src/stock_selection/universe/eligibility.py`
- `src/stock_selection/cli/main.py`
- `src/stock_selection/backtest/snapshots.py`
- `src/stock_selection/explainability/models.py`
- `tests/test_fmp_provider.py`
- `tests/test_universe.py`
- `tests/test_models.py`
- `requirements/session-handoff.md`
- `requirements/roadmap.md`
- `requirements/decisions.md`

Objective:
- Reconcile the current implementation against the repository docs, fix the single highest-value review batch, and leave a prioritized follow-up plan for remaining architecture and validation risks.

Findings:
1. Severity `P1`: provider and universe integrity had regressed from the documented contract. `FinancialModelingPrepProvider.list_securities(...)` invented `sector="unknown"` for exchange-only rows, and investability checks treated any non-`None` classification as sufficient peer classification.
   Recommended fix: make `Classification.sector` optional again, preserve exchange-only classifications honestly, and require at least one meaningful peer-group-defining field for `require_classification=True`.
   Dependencies: existing provider/universe tests.
   Acceptance criteria:
   - exchange-only FMP security rows do not fabricate sector data
   - exchange-only classification does not satisfy peer classification requirements
   - blank peer-classification strings are treated as missing
   - focused tests cover provider output, gating failure, and gating bypass when classification is optional
   Status: fixed in this session.
2. Severity `P1`: provider timing semantics are still under-specified for validation/backtesting safety. `list_securities(...)` and `get_peer_groups(...)` accept `as_of` but use latest-state endpoints without a contract-level distinction between latest-only and point-in-time-safe methods.
   Recommended fix: document latest-only behavior explicitly in provider contracts and FMP docstrings/comments, then add focused tests that guard against accidental point-in-time claims.
   Dependencies: none.
   Acceptance criteria:
   - latest-only provider methods are explicitly labeled as such at the contract boundary
   - focused tests or assertions verify that current behavior stays explicit rather than implied point-in-time safe
3. Severity `P2`: the repository still lacks the remaining pillar implementations and a true multi-pillar ranking path; current ranking support is limited to RP preview output and a hardcoded sample ranking CLI path.
   Recommended fix: continue milestone work incrementally, starting with the narrowest Growth pillar path, while keeping preview vs final ranking semantics explicit.
   Dependencies: completed normalization and RP contracts.
   Acceptance criteria:
   - new pillar paths remain deterministic and explicit about missing data
   - sample-only ranking paths are either clearly labeled or replaced when real multi-pillar assembly exists
   Status: fixed on 2026-03-18. The repo now includes all six deterministic pillar paths plus a composite ranking pipeline and pipeline-backed sample ranking exports.
4. Severity `P2`: explainability and backtest layers remain scaffolds, so validation-safety requirements from the docs are still mostly documented rather than implemented.
   Recommended fix: keep these deferred until later milestones, but continue treating look-ahead, turnover, cost, and benchmark alignment as explicit acceptance criteria before any validation claims.
   Dependencies: broader scoring and ranking pipeline.
   Acceptance criteria:
   - no code or docs imply backtest fidelity beyond the current scaffolded behavior
   Status: fixed on 2026-03-18 for the current audit scope. The repo now includes deterministic explanation-card generation and a validation harness with turnover, transaction costs, benchmark-relative excess returns, and explicit assumptions/limitations.
5. Severity `P3`: repo-wide Ruff still fails on two remaining `UP042` enum findings in `src/stock_selection/factors/registry.py`.
   Recommended fix: convert those enums to `StrEnum` in a dedicated lint batch.
   Dependencies: none.
   Acceptance criteria:
   - `uv run ruff check .` passes or fails only on issues outside the selected scope

Validation:
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run pyright`

Risks / open questions:
- The repo docs now largely match the implementation again, but provider timing semantics remain the biggest review-driven safety gap before deeper validation or backtesting work.
- Milestone 6 feature work is ready from an implementation standpoint, but the next review-driven batch is still valuable if we want the provider contract to be explicit before more pipeline depth accumulates.

Resume prompt:
- Read the baseline docs, then implement only the next review batch: make latest-only provider timing behavior explicit in the provider contracts and FMP adapter, add focused tests for that contract, run targeted checks plus `uv run ruff check .` and `uv run pyright`, and update handoff/roadmap/decisions/PLANS.

---

### 2026-03-17 — Review-Only Audit
Status: complete
Owner: Codex
Related files:
- `docs/audit-findings.md`
- `src/stock_selection/data/providers.py`
- `src/stock_selection/data/fmp.py`
- `src/stock_selection/cli/main.py`
- `src/stock_selection/backtest/snapshots.py`
- `src/stock_selection/explainability/models.py`
- `requirements/session-handoff.md`

Objective:
- Audit the committed implementation against the repository docs, record the highest-signal open issues, and leave a single recommended remediation batch.

Findings:
1. Severity `high`: provider timing semantics are still under-specified for point-in-time use.
   Recommended fix: make latest-only behavior explicit in provider contracts and the FMP adapter.
   Dependencies: none.
   Acceptance criteria:
   - latest-only methods are clearly marked at the contract boundary
   - focused tests guard against implied point-in-time behavior
2. Severity `medium`: the CLI still exposes a hardcoded sample ranking export that bypasses the implemented scoring path.
   Recommended fix: keep it clearly labeled as demo-only or replace it with a pipeline-backed consumer once broader ranking semantics exist.
   Dependencies: later ranking work or a docs-only clarification.
   Status: fixed on 2026-03-17 by replacing the public command with `export-demo-ranking`, retaining `export-sample-ranking` only as a hidden deprecated alias, and making RP export notices explicitly pipeline-backed versus preview-only.
   Acceptance criteria:
   - CLI command semantics are explicit and not misleading
3. Severity `medium`: the framework remains partial beyond the RP slice.
   Recommended fix: continue milestone work with the narrowest Growth pillar path, then add remaining pillars incrementally.
   Dependencies: completed RP/normalization contracts.
   Acceptance criteria:
   - each new pillar preserves deterministic missing-data behavior and focused tests
4. Severity `medium`: explainability and backtest layers remain scaffolds.
   Recommended fix: keep these deferred, but maintain explicit anti-bias requirements before any validation claims.
   Dependencies: broader scoring and ranking pipeline.
   Acceptance criteria:
   - no code or docs imply validation fidelity beyond current scaffold behavior
5. Severity `medium`: RP missing-data fallback semantics are explicit but still provisional.
   Recommended fix: revisit only when broader multi-pillar coverage policy is defined.
   Dependencies: later multi-pillar ranking work.
   Acceptance criteria:
   - future ranking semantics tests cover missing-data policy coherently across pillars
   Status: fixed on 2026-03-18. Missing normalized percentiles now remain explicit `None` scores, partial assemblies keep coverage/diagnostics visible, and final rankings exclude incompletely scored names instead of coercing them to `0.0`.
6. Severity `low`: repo-wide Ruff still fails on two registry enum findings.
   Recommended fix: convert the remaining registry enums to `StrEnum`.
   Dependencies: none.
   Acceptance criteria:
   - `uv run ruff check .` passes cleanly

Recommended first batch:
1. Fix `AUDIT-001` only.
2. Keep the change scoped to provider contracts, FMP method comments/contracts, and focused tests.
3. Do not start Growth or other pillar work in the same batch.
4. Status: completed on 2026-03-17. Latest-only timing semantics are now explicit in the provider contract and FMP adapter, with focused regression tests.

Recommended next batch:
1. Audit backlog complete on 2026-03-18.
2. Next work should return to milestone-driven validation realism and explainability depth rather than further audit cleanup.
