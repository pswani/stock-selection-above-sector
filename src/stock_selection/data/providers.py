from __future__ import annotations

from datetime import date
from typing import Protocol

import pandas as pd

from stock_selection.models import (
    EstimateSnapshot,
    FundamentalSnapshot,
    PeerGroup,
    PriceBar,
    Security,
)


class UniverseProvider(Protocol):
    def list_securities(self, as_of: date) -> list[Security]: ...


class ClassificationProvider(Protocol):
    def get_peer_groups(self, tickers: list[str], as_of: date) -> list[PeerGroup]: ...


class PriceDataProvider(Protocol):
    def get_price_history(self, tickers: list[str], start: date, end: date) -> list[PriceBar]: ...


class FundamentalsProvider(Protocol):
    def get_fundamentals(self, tickers: list[str], as_of: date) -> list[FundamentalSnapshot]: ...


class EstimatesProvider(Protocol):
    def get_estimates(self, tickers: list[str], as_of: date) -> list[EstimateSnapshot]: ...


def model_list_to_frame(records: list[object]) -> pd.DataFrame:
    return pd.DataFrame([getattr(record, "model_dump")() for record in records])
