# Code Review Guidance

## Purpose
This document defines how changes in this repository should be reviewed.

The goal is not only style compliance, but correctness, robustness, testability, and faithfulness to the stock-selection framework.

## Review priorities
Review in this order:
1. correctness
2. architecture fit
3. data and timing integrity
4. test quality
5. maintainability
6. style and polish

## Core review checklist

### 1. Correctness against repository docs
Check that the implementation matches:
- `docs/architecture.md`
- `docs/scoring-spec.md`
- `docs/validation-spec.md`
- relevant config files
- milestone acceptance criteria in `PLANS.md`

### 2. Scope discipline
- Is the change limited to the intended milestone?
- Were unrelated refactors introduced?
- Did the change modify public interfaces unnecessarily?

### 3. Schema and config robustness
- Are inputs validated?
- Are typed models used appropriately?
- Are configuration values validated and documented?
- Are defaults safe and explicit?

### 4. Data integrity and provider behavior
- Does the code clearly separate provider interfaces from business logic?
- Are unsupported provider capabilities handled honestly?
- Is missing data handled explicitly?
- Is timing of data availability respected?

### 5. Factor, scoring, and ranking logic
- Are formulas explicit and traceable?
- Are constants, weights, and thresholds configurable where appropriate?
- Is normalization documented and testable?
- Is ranking deterministic?
- Are ties, missing values, and partial coverage handled explicitly?
- Are penalties applied transparently?

### 6. Backtesting and validation safety
Review for:
- look-ahead bias
- survivorship bias
- leakage from future information
- timing misalignment between signals and tradability
- unrealistic rebalance assumptions
- omitted costs and turnover impact
- benchmark mismatch
- regime overfitting

### 7. Edge cases and failure behavior
- missing columns
- empty datasets
- partial sector coverage
- NaNs, infinities, duplicate securities, stale records, inconsistent dates

### 8. Test quality
- happy path coverage
- invalid input coverage
- missing-data coverage
- important edge cases
- integration tests for pipeline changes when needed

### 9. Maintainability
- readable code
- respected module boundaries
- clear naming
- minimal duplication
- reasonable function/class size
- useful docstrings

### 10. Documentation and handoff quality
- Were relevant docs updated?
- Were architectural or scoring decisions recorded?
- Was `requirements/session-handoff.md` updated?
- Is there an exact next prompt for resuming work?