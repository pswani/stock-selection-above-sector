"""Snapshot helpers for deterministic validation workflows.

These utilities still only write ranking snapshots, but they now complement the
validation harness rather than standing in for it. Point-in-time-safe data
alignment, richer execution assumptions, and broader benchmark logic remain
separate concerns for later milestones.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


def save_ranking_snapshot(frame: pd.DataFrame, as_of: date, output_dir: str | Path) -> Path:
    path = Path(output_dir) / f"ranking_snapshot_{as_of.isoformat()}.csv"
    frame.to_csv(path, index=False)
    return path
