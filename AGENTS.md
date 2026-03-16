# AGENTS.md

## Project goal
Build a Python application for sector-relative stock selection that identifies durable outperformance without relying on hype, weak quality, or fragile balance sheets.

## Working style for Codex
- For any medium or large task, start by reading `requirements/session-handoff.md`, `requirements/roadmap.md`, `requirements/decisions.md`, and `PLANS.md`.
- Use Plan mode before coding if the task touches architecture, provider design, pillar assembly, penalty logic, validation, or backtesting.
- Prefer the smallest high-value milestone over large unfocused changes.
- Do not invent market data, peer groups, formulas, or thresholds. If something is missing, add a TODO and document the gap.
- Avoid unrelated refactors.

## Architecture rules
- Scoring logic must remain deterministic and testable without network access.
- Providers are interfaces only; live adapters should remain isolated from factor and scoring code.
- Config drives weights, thresholds, and rule activation.
- Each factor or rule should have a clear definition, required inputs, and missing-data behavior.
- LLM usage is allowed for developer productivity, narrative explanations, and unstructured data extraction only.

## Files to keep updated
At the end of every non-trivial task update:
- `requirements/session-handoff.md`
- `requirements/decisions.md`
- `requirements/roadmap.md`
- `PLANS.md` if the task is part of a larger initiative

## End-of-session handoff format
Every non-trivial session must leave behind:
- Completed
- Current status
- Next task
- Known blockers
- Changed files
- Validation run
- Exact next prompt

## Quality gate
When changing code, try to run:
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run pyright`

If a command cannot run, say so in the handoff file.
