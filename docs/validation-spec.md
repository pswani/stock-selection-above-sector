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
- `src/stock_selection/backtest/snapshots.py` remains the snapshot export utility used alongside that harness.
- `src/stock_selection/explainability` now provides deterministic explanation-card generation from ranking outputs.

## Remaining limits
- The validation harness depends on externally supplied realized returns and benchmark returns; it does not solve point-in-time data sourcing by itself.
- Slippage, market impact, richer benchmark handling, and broader rebalance policies are still future work.
- No repo output should be described as production-ready validation evidence unless the timing-safety and execution-assumption gaps are explicitly addressed.
