from __future__ import annotations

import json
from datetime import date
from urllib.parse import urlencode
from urllib.request import urlopen

from stock_selection.models import (
    Classification,
    CorporateActionSnapshot,
    EstimateSnapshot,
    FundamentalSnapshot,
    OwnershipSnapshot,
    PeerGroup,
    PriceBar,
    Security,
    SecurityType,
)


class FmpProviderError(RuntimeError):
    pass


class FmpProviderUnsupportedCapabilityError(FmpProviderError):
    pass


class FinancialModelingPrepProvider:
    def __init__(self, api_key: str, base_url: str = "https://financialmodelingprep.com/api/v3") -> None:
        if not api_key:
            raise ValueError("FMP api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _get_json(self, path: str, query: dict[str, str | int | float] | None = None) -> list[dict] | dict:
        params: dict[str, str | int | float] = {"apikey": self.api_key}
        if query:
            params.update(query)
        url = f"{self.base_url}/{path.lstrip('/')}?{urlencode(params)}"

        try:
            with urlopen(url) as response:  # noqa: S310 - URL and host are controlled by config.
                payload = response.read().decode("utf-8")
        except Exception as exc:  # noqa: BLE001
            raise FmpProviderError(f"Failed request for {path}: {exc}") from exc

        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise FmpProviderError(f"Invalid JSON response for {path}") from exc

    def list_securities(self, as_of: date) -> list[Security]:
        # FMP list endpoint does not support point-in-time snapshots; it returns latest tradable list.
        data = self._get_json("stock/list")
        if not isinstance(data, list):
            return []

        results: list[Security] = []
        for row in data:
            ticker = row.get("symbol")
            if not ticker:
                continue
            exchange = row.get("exchangeShortName") or row.get("exchange")
            security_type = str(row.get("type", "")).lower()
            normalized_type = SecurityType.COMMON_STOCK
            if security_type == "etf":
                normalized_type = SecurityType.ETF
            elif security_type == "adr":
                normalized_type = SecurityType.ADR

            classification = None
            if exchange:
                classification = Classification(sector="unknown", exchange=exchange)

            results.append(
                Security(
                    ticker=ticker,
                    company_name=row.get("name"),
                    security_type=normalized_type,
                    currency="INR" if (row.get("currency") or "").upper() == "INR" else "USD",
                    classification=classification,
                    is_active=bool(row.get("isActivelyTrading", True)),
                )
            )
        return results

    def get_price_history(self, tickers: list[str], start: date, end: date) -> list[PriceBar]:
        bars: list[PriceBar] = []
        for ticker in tickers:
            payload = self._get_json(
                f"historical-price-full/{ticker}",
                query={"from": start.isoformat(), "to": end.isoformat()},
            )
            historical = payload.get("historical", []) if isinstance(payload, dict) else []
            for row in historical:
                bars.append(
                    PriceBar(
                        ticker=ticker,
                        as_of=date.fromisoformat(row["date"]),
                        open=row.get("open"),
                        high=row.get("high"),
                        low=row.get("low"),
                        close=row["close"],
                        adjusted_close=row.get("adjClose"),
                        volume=row.get("volume"),
                    )
                )
        return bars

    def get_fundamentals(self, tickers: list[str], as_of: date) -> list[FundamentalSnapshot]:
        snapshots: list[FundamentalSnapshot] = []
        for ticker in tickers:
            ratios = self._get_json(f"ratios-ttm/{ticker}")
            growth = self._get_json(f"financial-growth/{ticker}", query={"limit": 1})

            ratio_row = ratios[0] if isinstance(ratios, list) and ratios else {}
            growth_row = growth[0] if isinstance(growth, list) and growth else {}

            snapshots.append(
                FundamentalSnapshot(
                    ticker=ticker,
                    as_of=as_of,
                    revenue_growth_yoy=growth_row.get("revenueGrowth"),
                    eps_growth_yoy=growth_row.get("epsgrowth"),
                    operating_margin=ratio_row.get("operatingProfitMarginTTM"),
                    gross_margin=ratio_row.get("grossProfitMarginTTM"),
                    return_on_equity=ratio_row.get("returnOnEquityTTM"),
                    debt_to_equity=ratio_row.get("debtEquityRatioTTM"),
                    free_cash_flow_margin=None,
                    net_debt_to_ebitda=None,
                    diluted_share_count_growth_3y=None,
                )
            )
        return snapshots

    def get_estimates(self, tickers: list[str], as_of: date) -> list[EstimateSnapshot]:
        snapshots: list[EstimateSnapshot] = []
        for ticker in tickers:
            estimates = self._get_json(f"analyst-estimates/{ticker}", query={"limit": 1})
            ratios = self._get_json(f"ratios-ttm/{ticker}")

            estimate_row = estimates[0] if isinstance(estimates, list) and estimates else {}
            ratio_row = ratios[0] if isinstance(ratios, list) and ratios else {}

            snapshots.append(
                EstimateSnapshot(
                    ticker=ticker,
                    as_of=as_of,
                    forward_pe=ratio_row.get("peRatioTTM"),
                    peg_ratio=ratio_row.get("pegRatioTTM"),
                    price_to_sales=ratio_row.get("priceToSalesRatioTTM"),
                    ev_to_ebitda=ratio_row.get("enterpriseValueMultipleTTM"),
                    next_year_revenue_growth=estimate_row.get("estimatedRevenueAvg"),
                    next_year_eps_growth=estimate_row.get("estimatedEpsAvg"),
                    eps_revision_90d=None,
                    revenue_revision_90d=None,
                )
            )
        return snapshots

    def get_peer_groups(self, tickers: list[str], as_of: date) -> list[PeerGroup]:
        by_sector: dict[str, list[str]] = {}
        by_industry: dict[str, list[str]] = {}

        for ticker in tickers:
            profiles = self._get_json(f"profile/{ticker}")
            row = profiles[0] if isinstance(profiles, list) and profiles else {}
            sector = row.get("sector")
            industry = row.get("industry")
            if sector:
                by_sector.setdefault(sector, []).append(ticker)
            if industry:
                by_industry.setdefault(industry, []).append(ticker)

        groups: list[PeerGroup] = []
        for sector in sorted(by_sector):
            groups.append(PeerGroup(name=f"sector:{sector}", level="sector", members=sorted(by_sector[sector])))
        for industry in sorted(by_industry):
            groups.append(
                PeerGroup(name=f"industry:{industry}", level="industry", members=sorted(by_industry[industry]))
            )
        return groups

    def get_corporate_actions(
        self,
        tickers: list[str],
        start: date,
        end: date,
    ) -> list[CorporateActionSnapshot]:
        raise FmpProviderUnsupportedCapabilityError(
            "FMP corporate actions endpoint is not integrated yet in this milestone."
        )

    def get_ownership_and_short_interest(
        self,
        tickers: list[str],
        as_of: date,
    ) -> list[OwnershipSnapshot]:
        raise FmpProviderUnsupportedCapabilityError(
            "FMP ownership/short-interest endpoint is not integrated yet in this milestone."
        )
