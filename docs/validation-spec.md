# Validation Specification

## Required checks for each milestone
- unit tests for new logic
- config and schema validation tests if contracts changed
- deterministic behavior with sample fixtures
- explicit missing-data behavior

## When to add snapshot tests
Add snapshot-style comparisons when:
- a pillar returns stable outputs from fixed fixtures
- ranking exports become part of the contract
- penalty traces must remain human-auditable

## Non-goals for the starter
- live market integration validation
- production backtest benchmarking
- full data quality monitoring

## Current validation surface
- `src/stock_selection/backtest/validation.py` now provides a deterministic validation harness with explicit top-k selection, turnover, transaction costs, benchmark-relative excess returns, and stated assumptions/limitations.
- Validation reports now carry explicit benchmark metadata (`benchmark_type`, methodology, and return-alignment contract) so benchmark assumptions are inspectable in code and exports rather than only implied by a benchmark name string.
- `src/stock_selection/backtest/snapshots.py` remains the snapshot export utility used alongside that harness.
- `src/stock_selection/explainability` now provides deterministic explanation-card generation from ranking outputs, including structured top/weakest pillar details, missing-pillar disclosure, and penalty-rule disclosure.
- `src/stock_selection/reporting.py` now provides deterministic reporting/export helpers for validation summaries, validation periods, explanation cards, and validation-report CSV bundles so the new diagnostics are inspectable without ad hoc serialization.
- Pipeline-backed sample CLI exports now exist for explanation cards, validation reports, and a combined analysis bundle, while the demo ranking command remains explicitly demo-only.
- Underfilled periods now remain partially in cash instead of reweighting the available names to 100%; period results expose period index, requested-versus-selected counts, fill ratio, underfilled status, invested weight, cash weight, buy/sell turnover, next rebalance anchor, inferred holding-period days, and benchmark-relative gap in bps explicitly.
- Validation backtests now reject non-increasing period-input order instead of silently re-sorting dates, so period sequencing assumptions remain explicit at the call boundary.

## Remaining limits
- The validation harness depends on externally supplied realized returns and benchmark returns; it does not solve point-in-time data sourcing by itself.
- Slippage, market impact, richer benchmark handling, and broader rebalance policies are still future work.
- Cash currently earns an explicit `0.0` return when a period is underfilled; interest on idle capital is still future work.
- Benchmark series construction remains an external assumption; the harness now requires more explicit benchmark metadata, but it still does not infer or verify benchmark constituents or methodology from raw market data on its own.
- The final validation period still has no inferred period end unless a subsequent rebalance date is supplied.
- No repo output should be described as production-ready validation evidence unless the timing-safety and execution-assumption gaps are explicitly addressed.
