# stock-selection-starter-v3

Opinionated foundation for a Python application that implements a sector-relative stock selection framework for durable outperformance.

This repo is designed to work well with Codex across multiple computers by keeping the important context in files, standardizing the environment with `uv`, and leaving resumable checkpoints after each non-trivial session.

## What this version adds
- richer canonical Pydantic schemas for securities, prices, fundamentals, estimates, peer groups, factor outputs, pillar scores, and ranking results
- provider contracts with explicit capability boundaries
- scoring engine skeleton with score requests, score context, pillar interfaces, and scorecards
- penalty engine skeleton with configurable rules and trace output
- snapshot and report export CLI commands
- sample local CSV fixtures for early development
- stricter config validation and profile loading
- stronger tests around config, schemas, scoring, penalties, and CLI
- `PLANS.md` convention for large Codex initiatives

## Quick start
```bash
uv python install
uv sync --dev
uv run pytest -q
uv run stock-selection status
```

## Suggested first Codex prompt
Read:
- AGENTS.md
- PLANS.md
- requirements/session-handoff.md
- requirements/roadmap.md
- requirements/decisions.md
- docs/architecture.md
- docs/scoring-spec.md
- docs/validation-spec.md

Then:
1. summarize the current repo state in 6 to 8 bullets
2. identify the next smallest high-value milestone
3. implement only that milestone
4. add or update tests
5. update requirements/session-handoff.md and PLANS.md with the exact next resume prompt

## Repo principles
- Keep business logic deterministic and testable.
- Keep factor definitions explicit in docs and config.
- Keep provider integrations abstract until the scoring core is stable.
- Use small, checkpointed Codex sessions.
