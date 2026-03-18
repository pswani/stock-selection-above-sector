# Scoring Specification

This file describes the opinionated scoring foundation included in v3.

## Pillars
The system assumes six pillars:
- `RP` Relative Performance
- `G` Growth
- `Q` Quality
- `V` Valuation
- `R` Risk
- `S` Sentiment / estimate revision support

## Scoring flow
1. Gather canonical input snapshots
2. Compute factors
3. Normalize factors relative to peer groups
4. Compute pillar scores
5. Combine pillar scores with a profile
6. Apply penalties
7. Produce a final ranking result with traces

## Included scaffolding
- `ScoreRequest` defines as-of date, profile, universe, and optional notes
- `ScoreContext` carries the request, config profile, and optional trace flags
- `PillarEngine` is the interface for a pillar implementation and now derives score maps from score cards
- `Scorecard` carries raw pillar scores, weighted score, penalties, and final score
- `PenaltyTrace` records which rules fired and why

## Current status
This repo includes interfaces, typed models, and baseline composite / penalty orchestration. Full factor formulas remain intentionally incomplete so Codex can implement them milestone by milestone.
Milestone 4 now includes a complete normalization handoff from `FactorObservation` outputs into typed normalized factor observations, with deterministic DataFrame projections available for downstream consumers before any pillar scoring is applied.
Milestone 5 is now complete for Relative Performance: the RP path builds `relative_strength_6m` factor observations, converts normalized outputs into `PillarScoreCard` results with diagnostics and coverage, groups those score cards into deterministic partial assemblies, and exposes an RP-only preview ranking/export path that remains explicit about incomplete multi-pillar coverage.
Milestone 6 has now started with a narrow Growth slice: the repo includes a `revenue_growth_yoy` Growth pillar path that mirrors the RP contract by building typed factor observations from fundamental snapshots, normalizing them by peer group, and emitting deterministic `PillarScoreCard` outputs without claiming a final multi-pillar ranking.
