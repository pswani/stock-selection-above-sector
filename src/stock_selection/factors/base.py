from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from stock_selection.models import FactorObservation
from stock_selection.normalize.factors import normalize_factor_observations


@dataclass(slots=True)
class FactorInputBundle:
    as_of: date
    tickers: list[str]


class FactorCalculator:
    name: str

    def compute(self, bundle: FactorInputBundle) -> list[FactorObservation]:
        raise NotImplementedError


def normalize_factor_output(
    observations: list[FactorObservation],
) -> pd.DataFrame:
    return normalize_factor_observations(observations)
