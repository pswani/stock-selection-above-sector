# Data Dictionary

## Canonical entities

### Security
Basic instrument metadata and sector classification.

### PeerGroup
Named comparison set used for sector-relative normalization.

### PriceBar
Daily price and volume information.

### FundamentalSnapshot
Point-in-time fundamental metrics used by quality, growth, and risk factors.

### EstimateSnapshot
Forward-looking valuation and revision metrics.

### FactorObservation
A computed factor value with metadata about direction and peer group.

### PillarScoreCard
A pillar score with optional coverage and diagnostics.

### RankingResult
The final ranked output after weighting and penalties.

## Fixture files
- `data/sample/securities.csv`
- `data/sample/fundamentals.csv`
- `data/sample/estimates.csv`

These are intentionally small starter fixtures for development and testing.
