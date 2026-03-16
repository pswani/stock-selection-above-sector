from __future__ import annotations

from pathlib import Path

import pandas as pd


SAMPLE_DIR = Path("data/sample")


def load_sample_csv(name: str, root: Path = SAMPLE_DIR) -> pd.DataFrame:
    return pd.read_csv(root / name)
