# Session Handoff

## Completed
- Fixed `AUDIT-002` by tightening the CLI/export contract around ranking outputs without starting other milestone work.
- Replaced the misleading public `export-sample-ranking` command with an explicit `export-demo-ranking` command for hardcoded ranking rows.
- Kept `export-sample-ranking` only as a hidden backward-compatible alias that prints a deprecation warning and states that it is demo-only.
- Made the pipeline-backed RP exports print explicit contract notices so the CLI now distinguishes:
  - demo-only ranking export
  - pipeline-backed RP pillar export
  - pipeline-backed RP preview export that is still not a final multi-pillar ranking
- Added focused CLI regression coverage for the changed command contract path.

## Current status
- `AUDIT-002` is complete in changed scope: the public CLI now makes demo-only versus pipeline-backed exports explicit.
- The repo still includes completed normalization plus a narrow end-to-end RP slice, but true multi-pillar ranking remains unimplemented.
- Remaining gaps are primarily:
- only RP is implemented end-to-end; the remaining pillars and true multi-pillar ranking are still absent (`AUDIT-003`)
- explainability and backtest layers are still scaffolds (`AUDIT-004`)
- RP missing-data fallback semantics are explicit but still provisional (`AUDIT-005`)
- `uv run pytest -q` passed in this session.
- `uv run pyright` passed in this session.
- `uv run ruff check .` still fails only on 2 pre-existing `UP042` findings in `src/stock_selection/factors/registry.py` (`AUDIT-006`).

## Next task
- Recommended next task: continue milestone work with `AUDIT-003` only by implementing the narrowest next pillar path, while preserving the explicit preview-versus-final ranking contract established in this session.

## Known blockers
- `uv run ruff check .` currently fails on 2 pre-existing `UP042` findings in:
  - `src/stock_selection/factors/registry.py`

## Changed files
- `src/stock_selection/cli/main.py`
- `tests/test_cli.py`
- `requirements/session-handoff.md`
- `requirements/roadmap.md`
- `requirements/decisions.md`
- `PLANS.md`

## Validation run
- `uv run pytest -q tests/test_cli.py tests/test_reporting.py` (passed)
- `uv run pytest -q` (passed)
- `uv run ruff check src/stock_selection/cli/main.py tests/test_cli.py` (passed)
- `uv run ruff check .` (failed only on 2 pre-existing `UP042` violations in `src/stock_selection/factors/registry.py`)
- `uv run pyright` (passed: `0 errors`)
- `uv run pyright src/stock_selection/cli/main.py tests/test_cli.py` (passed: `0 errors`)

## Hardening status
- Highest-value hardening changes implemented:
  - explicit public demo-only ranking command
  - backward-compatible hidden alias with deprecation warning
  - explicit pipeline-backed notices for RP exports
- What remains:
  - `AUDIT-003`
  - `AUDIT-004`
  - `AUDIT-005`
  - `AUDIT-006`

## Exact next prompt
Read:
- AGENTS.md
- PLANS.md
- requirements/session-handoff.md
- requirements/roadmap.md
- requirements/decisions.md
- docs/architecture.md
- docs/scoring-spec.md
- docs/validation-spec.md
- docs/code_review.md

Then:
1. implement only the next remediation batch: fix `AUDIT-003`
2. keep the work scoped to the narrowest next pillar path without inventing a final multi-pillar ranking
3. preserve the explicit preview-versus-final CLI/export semantics established for `AUDIT-002`
4. add/update focused tests only for the changed pillar and scoring path
5. avoid unrelated refactors
6. run targeted tests plus `uv run pytest -q`, `uv run ruff check .`, and `uv run pyright`
7. fix defects found in the changed scope
8. update `requirements/session-handoff.md`, `requirements/roadmap.md`, `requirements/decisions.md`, and `PLANS.md` with results
