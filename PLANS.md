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

5. **Milestone 5 — Relative Performance (RP) pillar end-to-end (current)**
   - Scope: first complete pillar from factor inputs to normalized pillar score.
   - Acceptance criteria: RP score card produced with diagnostics and coverage ratio.
   - Tests: unit tests + integration test through composite assembly.
   - Dependencies: Milestones 1-4.

6. **Milestone 6 — Remaining pillars (G, Q, V, R, S) incremental**
   - Scope: implement one pillar per sub-step with explicit formulas and missing-data behavior.
   - Acceptance criteria: all six pillars produce deterministic score cards with traces.
   - Tests: per-pillar unit tests and integration checks.
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
   - Dependencies: Milestones 1-7.

9. **Milestone 9 — Validation/backtest harness**
   - Scope: monthly/quarterly rebalance, sector-neutral/global top-k, benchmark comparison, turnover/cost model, anti-bias guards, false-positive and regime tests.
   - Acceptance criteria: reproducible validation run from fixtures with documented assumptions/limits.
   - Tests: integration/snapshot tests for backtest outputs and guardrails.
   - Dependencies: Milestones 1-8.

10. **Milestone 10 — CLI/reporting/export workflow hardening**
    - Scope: finalize CLI entry points for scoring, ranking, export, validation reports.
    - Acceptance criteria: documented CLI workflow runs end-to-end on sample fixtures.
    - Tests: CLI smoke tests + export contract tests.
    - Dependencies: Milestones 1-9.

Validation per milestone:
- `uv run pytest -q` (or targeted tests for changed modules)
- `uv run ruff check .`
- `uv run pyright`

Risks / open questions:
- Final factor formulas/threshold calibrations are still pending and must remain config-driven.
- FMP adapter is now the primary provider entry point; provider-contract expansion is complete, and the next delivery risk shifts to documenting and implementing deterministic peer-relative normalization behavior for small/incomplete groups.
- The normalized-factor contract is now typed; the next delivery risk is choosing the smallest RP pillar inputs/formulas that use it without prematurely generalizing for later pillars.
- Environment initialization reproducibility is addressed with bootstrap/validation scripts; keep these scripts aligned with `uv.lock`, `.python-version`, and the full runtime/dev dependency set as dependencies change, and keep `validate-env.sh` self-contained for fresh servers.

Resume prompt:
- Continue the active plan in `PLANS.md` at "2026-03-16 — Full stock-selection framework implementation", start Milestone 5 only by implementing the narrowest end-to-end Relative Performance pillar path on top of the completed normalization contract, then update handoff/roadmap/decisions after running tests.
