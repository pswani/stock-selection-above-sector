from datetime import date

import pytest

from stock_selection.data.fmp import (
    FinancialModelingPrepProvider,
    FmpProviderError,
    FmpProviderUnsupportedCapabilityError,
)
from stock_selection.data.providers import build_primary_provider


class StubFmpProvider(FinancialModelingPrepProvider):
    def __init__(self) -> None:
        super().__init__(api_key="demo")

    def _get_json(self, path: str, query=None):  # type: ignore[override]
        if path.startswith("historical-price-full/stock_dividend/"):
            return {
                "historical": [
                    {"date": "2026-01-10", "dividend": 0.75},
                    {"date": "2026-01-20", "adjDividend": "0.80"},
                ]
            }
        if path.startswith("historical-price-full/stock_split/"):
            return {
                "historical": [
                    {"date": "2026-01-15", "splitRatio": "3:2"},
                ]
            }
        if path == "stock/list":
            return [
                {
                    "symbol": "MSFT",
                    "name": "Microsoft",
                    "currency": "USD",
                    "exchangeShortName": "NASDAQ",
                    "type": "stock",
                    "isActivelyTrading": True,
                }
            ]
        if path.startswith("historical-price-full/"):
            return {
                "historical": [
                    {
                        "date": "2026-01-30",
                        "open": 100.0,
                        "high": 110.0,
                        "low": 95.0,
                        "close": 105.0,
                        "adjClose": 104.5,
                        "volume": 1234,
                    }
                ]
            }
        if path.startswith("ratios-ttm/"):
            return [
                {
                    "peRatioTTM": 22.0,
                    "pegRatioTTM": 1.2,
                    "priceToSalesRatioTTM": 4.0,
                    "enterpriseValueMultipleTTM": 12.0,
                    "operatingProfitMarginTTM": 0.32,
                    "grossProfitMarginTTM": 0.7,
                    "returnOnEquityTTM": 0.3,
                    "debtEquityRatioTTM": 0.4,
                }
            ]
        if path.startswith("financial-growth/"):
            return [{"revenueGrowth": 0.1, "epsgrowth": 0.2}]
        if path.startswith("analyst-estimates/"):
            return [{"estimatedRevenueAvg": 0.11, "estimatedEpsAvg": 0.15}]
        if path.startswith("profile/"):
            return [{"sector": "Information Technology", "industry": "Software"}]
        if path.startswith("key-metrics-ttm/"):
            return [
                {
                    "institutionalOwnershipPercentageTTM": "0.72",
                    "insiderOwnershipPercentageTTM": 0.11,
                }
            ]
        if path.startswith("short-interest/"):
            return [{"shortPercentOfFloat": "0.034"}]
        return []


class MissingDataStubFmpProvider(FinancialModelingPrepProvider):
    def __init__(self) -> None:
        super().__init__(api_key="demo")

    def _get_json(self, path: str, query=None):  # type: ignore[override]
        if path.startswith("historical-price-full/stock_dividend/"):
            return {"historical": [{"date": "2026-01-10", "dividend": None}]}
        if path.startswith("historical-price-full/stock_split/"):
            return {"historical": [{"date": "2026-01-15"}]}
        if path.startswith("key-metrics-ttm/"):
            return [{}]
        if path.startswith("short-interest/"):
            return [{}]
        return []


class UnsupportedEndpointStubFmpProvider(FinancialModelingPrepProvider):
    def __init__(self) -> None:
        super().__init__(api_key="demo")

    def _get_json(self, path: str, query=None):  # type: ignore[override]
        if path.startswith("historical-price-full/stock_dividend/"):
            raise FmpProviderError("dividend endpoint unavailable")
        if path.startswith("historical-price-full/stock_split/"):
            raise FmpProviderError("split endpoint unavailable")
        if path.startswith("key-metrics-ttm/"):
            raise FmpProviderError("key metrics endpoint unavailable")
        if path.startswith("short-interest/"):
            raise FmpProviderError("short interest endpoint unavailable")
        return []


def test_fmp_provider_parses_price_fundamental_and_estimate_snapshots() -> None:
    provider = StubFmpProvider()

    prices = provider.get_price_history(["MSFT"], start=date(2026, 1, 1), end=date(2026, 1, 31))
    fundamentals = provider.get_fundamentals(["MSFT"], as_of=date(2026, 1, 31))
    estimates = provider.get_estimates(["MSFT"], as_of=date(2026, 1, 31))

    assert prices[0].ticker == "MSFT"
    assert prices[0].close == 105.0
    assert fundamentals[0].return_on_equity == 0.3
    assert fundamentals[0].revenue_growth_yoy == 0.1
    assert estimates[0].forward_pe == 22.0
    assert estimates[0].next_year_eps_growth == 0.15


def test_fmp_provider_uses_fundamental_and_estimate_alias_fallbacks() -> None:
    class FundamentalEstimateAliasStubProvider(FinancialModelingPrepProvider):
        def __init__(self) -> None:
            super().__init__(api_key="demo")

        def _get_json(self, path: str, query=None):  # type: ignore[override]
            if path.startswith("ratios-ttm/"):
                return [
                    {
                        "priceEarningsRatioTTM": "19.5",
                        "pegRatio": "1.4",
                        "priceToSalesTTM": "3.9",
                        "evToEbitdaTTM": "10.2",
                        "operatingMarginTTM": "0.25",
                        "grossMarginTTM": "0.61",
                        "returnOnEquity": "0.18",
                        "debtToEquity": "0.42",
                    }
                ]
            if path.startswith("financial-growth/"):
                return [{"growthRevenue": "0.09", "epsGrowth": "0.12"}]
            if path.startswith("analyst-estimates/"):
                return [{"estimatedRevenueGrowth": "0.08", "estimatedEpsGrowth": "0.11"}]
            return []

    provider = FundamentalEstimateAliasStubProvider()

    fundamentals = provider.get_fundamentals(["MSFT"], as_of=date(2026, 1, 31))
    estimates = provider.get_estimates(["MSFT"], as_of=date(2026, 1, 31))

    assert fundamentals[0].revenue_growth_yoy == 0.09
    assert fundamentals[0].eps_growth_yoy == 0.12
    assert fundamentals[0].operating_margin == 0.25
    assert fundamentals[0].gross_margin == 0.61
    assert fundamentals[0].return_on_equity == 0.18
    assert fundamentals[0].debt_to_equity == 0.42

    assert estimates[0].forward_pe == 19.5
    assert estimates[0].peg_ratio == 1.4
    assert estimates[0].price_to_sales == 3.9
    assert estimates[0].ev_to_ebitda == 10.2
    assert estimates[0].next_year_revenue_growth == 0.08
    assert estimates[0].next_year_eps_growth == 0.11


def test_fmp_provider_uses_non_ttm_ratio_alias_fallbacks() -> None:
    class NonTtmRatioAliasStubProvider(FinancialModelingPrepProvider):
        def __init__(self) -> None:
            super().__init__(api_key="demo")

        def _get_json(self, path: str, query=None):  # type: ignore[override]
            if path.startswith("ratios-ttm/"):
                return [
                    {
                        "peRatio": "18.5",
                        "priceToSalesRatio": "3.4",
                        "enterpriseValueMultiple": "9.8",
                        "operatingProfitMargin": "0.22",
                        "grossProfitMargin": "0.58",
                        "debtEquityRatio": "0.37",
                    }
                ]
            if path.startswith("financial-growth/"):
                return [{}]
            if path.startswith("analyst-estimates/"):
                return [{}]
            return []

    provider = NonTtmRatioAliasStubProvider()

    fundamentals = provider.get_fundamentals(["MSFT"], as_of=date(2026, 1, 31))
    estimates = provider.get_estimates(["MSFT"], as_of=date(2026, 1, 31))

    assert fundamentals[0].operating_margin == 0.22
    assert fundamentals[0].gross_margin == 0.58
    assert fundamentals[0].debt_to_equity == 0.37

    assert estimates[0].forward_pe == 18.5
    assert estimates[0].price_to_sales == 3.4
    assert estimates[0].ev_to_ebitda == 9.8


def test_fmp_provider_builds_peer_groups() -> None:
    provider = StubFmpProvider()
    groups = provider.get_peer_groups(["MSFT", "ADBE"], as_of=date(2026, 1, 31))

    assert len(groups) == 2
    by_level = {group.level: group for group in groups}
    assert by_level["industry"].members == ["ADBE", "MSFT"]
    assert by_level["sector"].members == ["ADBE", "MSFT"]


def test_build_primary_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STOCK_SELECTION_FMP_API_KEY", raising=False)

    with pytest.raises(ValueError, match="Missing FMP API key"):
        build_primary_provider()


def test_fmp_provider_parses_corporate_actions() -> None:
    provider = StubFmpProvider()
    snapshots = provider.get_corporate_actions(
        ["MSFT"],
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    assert [(snapshot.action_type, snapshot.value) for snapshot in snapshots] == [
        ("dividend", 0.75),
        ("split", 1.5),
        ("dividend", 0.8),
    ]


def test_fmp_provider_parses_ownership_and_short_interest() -> None:
    provider = StubFmpProvider()
    snapshots = provider.get_ownership_and_short_interest(
        ["MSFT"],
        as_of=date(2026, 1, 31),
    )

    assert len(snapshots) == 1
    assert snapshots[0].institutional_ownership == 0.72
    assert snapshots[0].insider_ownership == 0.11
    assert snapshots[0].short_interest_percent_float == 0.034


def test_fmp_provider_preserves_missing_corporate_action_and_ownership_fields() -> None:
    provider = MissingDataStubFmpProvider()

    corporate_actions = provider.get_corporate_actions(
        ["MSFT"],
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )
    ownership = provider.get_ownership_and_short_interest(
        ["MSFT"],
        as_of=date(2026, 1, 31),
    )

    assert [snapshot.value for snapshot in corporate_actions] == [None, None]
    assert ownership[0].institutional_ownership is None
    assert ownership[0].insider_ownership is None
    assert ownership[0].short_interest_percent_float is None


def test_fmp_provider_uses_non_ttm_ownership_fallback_fields() -> None:
    class OwnershipFallbackStubProvider(FinancialModelingPrepProvider):
        def __init__(self) -> None:
            super().__init__(api_key="demo")

        def _get_json(self, path: str, query=None):  # type: ignore[override]
            if path.startswith("key-metrics-ttm/"):
                return [{"institutionalOwnership": "0.67", "insiderOwnership": 0.09}]
            if path.startswith("short-interest/"):
                return [{"shortOutstandingPercent": "0.021"}]
            return []

    provider = OwnershipFallbackStubProvider()
    snapshots = provider.get_ownership_and_short_interest(
        ["MSFT"],
        as_of=date(2026, 1, 31),
    )

    assert snapshots[0].institutional_ownership == 0.67
    assert snapshots[0].insider_ownership == 0.09
    assert snapshots[0].short_interest_percent_float == 0.021


def test_fmp_provider_explicitly_reports_unsupported_corporate_actions() -> None:
    provider = UnsupportedEndpointStubFmpProvider()

    with pytest.raises(FmpProviderUnsupportedCapabilityError, match="corporate actions"):
        provider.get_corporate_actions(
            ["MSFT"],
            start=date(2026, 1, 1),
            end=date(2026, 1, 31),
        )


def test_fmp_provider_explicitly_reports_unsupported_ownership() -> None:
    provider = UnsupportedEndpointStubFmpProvider()

    with pytest.raises(FmpProviderUnsupportedCapabilityError, match="ownership/short-interest"):
        provider.get_ownership_and_short_interest(
            ["MSFT"],
            as_of=date(2026, 1, 31),
        )
