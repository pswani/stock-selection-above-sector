# Architecture

## Intent
This repository provides an opinionated foundation for a sector-relative stock selection system. The goal is to give Codex strong structure without prematurely locking in every formula or data source.

## Core layers
1. **Universe and classification**
   - Security master
   - Sector / industry / peer group mapping
   - Eligibility filters
2. **Data access layer**
   - Price data provider
   - Fundamentals provider
   - Estimates provider
   - Classification provider
3. **Feature and factor layer**
   - Deterministic factor computation
   - Factor metadata and traceability
   - `FactorObservation` outputs as the normalization handoff contract
4. **Normalization layer**
   - Sector-relative normalization
   - Percentiles / z-scores / winsorization
   - Explicit coverage and missing-data status by peer group
   - Typed normalized-factor outputs plus DataFrame projections derived from them
5. **Scoring layer**
   - Pillar interfaces
   - Pillar score cards as the diagnostic scoring contract
   - Partial pillar-score assembly before full composite ranking exists
   - Composite score assembly
   - Profile-based weighting
6. **Penalty layer**
   - Rule-based penalties
   - Penalty traces and diagnostics
7. **Ranking and reporting layer**
   - Ranked results
   - Snapshot exports
   - Pillar score card exports
   - Human-readable reports
8. **Validation layer**
   - Unit tests
   - Reproducible sample fixtures
   - Backtest and snapshot comparison hooks

## Deliberate boundaries
- Provider interfaces should not depend on scoring internals.
- Factor and scoring code should accept typed models or DataFrames derived from typed models.
- Export code should consume ranking results, not raw provider payloads.
- Penalty application should be explicit and separately testable.

## Development order
1. canonical schemas
2. provider contracts
3. normalization utilities
4. one pillar end to end
5. penalty engine wiring
6. ranking result export
7. provider adapters
8. validation / backtesting expansion
