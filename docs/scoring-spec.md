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
Milestone 6 now covers all six pillars with deterministic single-factor paths:
- `RP` via `relative_strength_6m`
- `G` via `revenue_growth_yoy`
- `Q` via `return_on_equity`
- `V` via `forward_pe`
- `R` via `volatility_3m`
- `S` via `eps_revision_90d`

The repo now also includes a composite ranking pipeline that scores all six pillars, assembles complete pillar sets, applies configured weights and penalties, and emits deterministic final `RankingResult` outputs. The RP preview path remains explicit preview output, while the composite ranking path is now the implemented final ranking surface.

## Missing-data policy
- `PillarScoreCard.score` stays `None` when peer normalization cannot produce a percentile; missing scores are no longer coerced to `0.0`.
- Pillar diagnostics and coverage remain populated even when the score is missing, so exports still explain whether the cause was `missing_value`, `missing_peer_group`, or `insufficient_peer_group`.
- Composite assembly counts only scored pillars toward `available_pillar_count` and `min_required_pillars`.
- Final composite rankings therefore exclude incompletely scored names under the current six-pillar profile settings, while assembly and preview outputs still surface those names explicitly.
