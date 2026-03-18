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

## Current scaffold limits
- `src/stock_selection/backtest/snapshots.py` writes deterministic snapshot files only; it is not a validated backtest engine.
- `src/stock_selection/explainability/models.py` provides placeholder explanation-card schemas only; it is not yet a full explainability contract.
- Until later milestones add turnover, transaction costs, benchmark alignment, and timing-safe data contracts, no repo output should be described as production-ready validation or backtest evidence.
