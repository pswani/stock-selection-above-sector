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
- `PillarEngine` is the interface for a pillar implementation
- `Scorecard` carries raw pillar scores, weighted score, penalties, and final score
- `PenaltyTrace` records which rules fired and why

## Current status
This repo includes interfaces, typed models, and baseline composite / penalty orchestration. Full factor formulas remain intentionally incomplete so Codex can implement them milestone by milestone.
