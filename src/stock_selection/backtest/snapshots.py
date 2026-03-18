"""Snapshot-only helpers for reporting intermediate ranking artifacts.

These utilities write deterministic CSV outputs for inspection, but they do not
constitute a full backtest harness. Turnover, transaction costs, benchmark
alignment, and point-in-time execution safety remain out of scope here until
Milestone 9.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


def save_ranking_snapshot(frame: pd.DataFrame, as_of: date, output_dir: str | Path) -> Path:
    path = Path(output_dir) / f"ranking_snapshot_{as_of.isoformat()}.csv"
    frame.to_csv(path, index=False)
    return path
