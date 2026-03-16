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
./scripts/bootstrap.sh
uv run stock-selection status
```

## Environment validation
```bash
./scripts/validate-env.sh
```

`validate-env.sh` also performs `uv sync --dev --frozen` so it can run consistently on newly provisioned servers where bootstrap may not have been run yet.

Both scripts are deterministic and intended for fresh server initialization. `bootstrap.sh` uses `.python-version` and `uv.lock` (`uv sync --dev --frozen`) to avoid environment drift, validates runtime packages (`numpy`, `pandas`, `pydantic`, `pydantic_settings`, `scipy`, `sklearn`, `pyyaml`, `typer`, `rich`), and verifies dev tools (`pytest`, `ruff`, `pyright`).


## Data provider
- Primary provider: Financial Modeling Prep (FMP) adapter (`stock_selection.data.FinancialModelingPrepProvider`).
- Set API key in `.env` as `STOCK_SELECTION_FMP_API_KEY=your_key_here`.
- Optional base URL override: `STOCK_SELECTION_FMP_BASE_URL=https://financialmodelingprep.com/api/v3`.

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
