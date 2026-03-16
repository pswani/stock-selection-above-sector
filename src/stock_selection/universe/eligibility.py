from __future__ import annotations

from stock_selection.models import Security


def filter_active_common_stocks(securities: list[Security]) -> list[Security]:
    return [security for security in securities if security.is_active and security.security_type.value == "common_stock"]
