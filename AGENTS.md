# AGENTS.md

## Project goal
Build a Python application for sector-relative stock selection that identifies durable outperformance without relying on hype, weak quality, or fragile balance sheets.

The system must be:
- modular
- deterministic where possible
- testable
- resumable across Codex sessions
- portable across developer machines using `uv`
- honest about missing data and unsupported assumptions

## Source of truth
When working in this repository, read these files first when they exist:

1. `AGENTS.md`
2. `PLANS.md`
3. `requirements/session-handoff.md`
4. `requirements/roadmap.md`
5. `requirements/decisions.md`
6. `docs/architecture.md`
7. `docs/scoring-spec.md`
8. `docs/validation-spec.md`
9. `docs/code_review.md`

If there is a conflict, prefer:
1. explicit user instruction
2. this file
3. architecture and scoring docs
4. local code comments and tests

## Working style for Codex
- For any medium or large task, start by reading `requirements/session-handoff.md`, `requirements/roadmap.md`, `requirements/decisions.md`, and `PLANS.md`.
- Use Plan mode before coding if the task touches architecture, provider design, pillar assembly, penalty logic, validation, or backtesting.
- Prefer the smallest high-value milestone over large unfocused changes.
- Do not invent market data, peer groups, formulas, or thresholds. If something is missing, add a TODO and document the gap.
- Avoid unrelated refactors.
- Prefer correctness over speed.
- Prefer explicitness over cleverness.
- Prefer reviewable incremental changes over broad rewrites.
- Prefer configuration-driven behavior over hardcoded business logic.

## Architecture rules
- Scoring logic must remain deterministic and testable without network access.
- Providers are interfaces only; live adapters should remain isolated from factor and scoring code.
- Config drives weights, thresholds, and rule activation.
- Each factor or rule should have a clear definition, required inputs, and missing-data behavior.
- LLM usage is allowed for developer productivity, narrative explanations, and unstructured data extraction only.

Maintain clear separation between:
- provider interfaces
- raw data ingestion
- canonical schemas
- factor computation
- normalization
- scoring
- penalties
- explainability
- backtesting
- CLI / reporting

## Python and tooling standards
Use the repository's `uv` workflow.

### Environment
- Respect `.python-version`
- Use `uv sync --dev` for setup
- Use `uv run ...` for commands

### Typical commands
- `uv sync --dev`
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run ruff format .`
- `uv run pyright`

If a command fails because a tool is not yet configured, fix the project configuration only if it is in scope for the current milestone. Otherwise record it in the handoff.

## Implementation expectations
- Work on only one milestone at a time.
- Implement the smallest high-value increment first.
- Reuse existing abstractions where reasonable.
- Keep functions small and composable.
- Avoid magic constants.
- Prefer typed models and validated config.
- Do not simulate unavailable live data as if it were real.
- If something is underspecified, make the smallest safe implementation, add a TODO if needed, and document the gap.

## Review expectations
After implementation, perform a self-review against:
- `docs/architecture.md`
- `docs/scoring-spec.md`
- `docs/validation-spec.md`
- `docs/code_review.md`

The review should check:
- correctness against documented design
- hidden assumptions
- schema robustness
- edge cases
- missing-data handling
- regression risk in changed scope
- unnecessary complexity
- test gaps

## Testing expectations
At minimum for changed scope:
- add or update unit tests
- run unit tests relevant to touched modules
- run broader integration tests when pipeline behavior changes
- ensure new config and schema behavior is validated

When practical, also run:
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run pyright`

Do not claim something is tested unless tests were actually run.

## Backtesting and validation safety
Guard against:
- look-ahead bias
- survivorship bias
- leakage
- unrealistic turnover assumptions
- omitted transaction costs
- benchmark mismatch
- overfitting to narrow periods

Any backtesting-related change should note assumptions and limitations.

## Files to keep updated
At the end of every non-trivial task update:
- `requirements/session-handoff.md`
- `requirements/decisions.md`
- `requirements/roadmap.md`
- `PLANS.md` if the task is part of a larger initiative

Also update docs when behavior, interfaces, assumptions, or architecture change:
- `docs/architecture.md`
- `docs/scoring-spec.md`
- `docs/validation-spec.md`
- `docs/code_review.md` if review policy changes

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

## Definition of done for a milestone
A milestone is done when:
- acceptance criteria are met
- code is added in the intended module boundaries
- tests for changed behavior exist
- relevant checks were run
- defects in changed scope were fixed
- docs and handoff files were updated

## Scope control
Do not:
- rewrite large parts of the repo without necessity
- change public interfaces casually
- mix unrelated cleanup with milestone work
- silently change formulas or thresholds
- over-engineer prematurely