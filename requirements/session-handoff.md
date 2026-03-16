# Session Handoff

## Completed
- Created opinionated foundation with richer schemas, provider contracts, scoring and penalty skeletons, export CLI, and sample fixtures.

## Current status
- Ready for the first milestone implementation using Codex.

## Next task
- Implement canonical factor schemas and a factor registry with tests.

## Known blockers
- Real market data provider selection is still open.
- Exact factor formulas and thresholds remain to be implemented from the framework spec.

## Changed files
- starter repo foundation files

## Validation run
- `pytest -q`

## Exact next prompt
Read:
- AGENTS.md
- PLANS.md
- requirements/session-handoff.md
- requirements/roadmap.md
- requirements/decisions.md
- docs/architecture.md
- docs/scoring-spec.md

Then:
1. summarize the current repo state in 6 to 8 bullets
2. implement canonical factor schemas and a factor registry
3. add tests for validation and registration behavior
4. avoid unrelated refactors
5. update requirements/session-handoff.md and PLANS.md with the exact next resume prompt
