from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class SaleLotRow:
    transaction_id: str
    sale_date: str
    settlement_date: str
    sale_price_usd: Decimal | None
    acquisition_date: str
    shares_sold: Decimal | None
    cost_basis_per_share_usd: Decimal | None
    total_cost_basis_usd: Decimal | None
    total_sale_proceeds_usd: Decimal | None
    gain_loss_usd: Decimal | None
    commission_usd: Decimal | None
    fees_usd: Decimal | None
    net_proceeds_usd: Decimal | None
    proceeds_currency: str
    converted_net_proceeds: Decimal | None

    @classmethod
    def csv_headers(cls) -> list[str]:
        return [
            "sale_date",
            "settlement_date",
            "sale_price_usd",
            "acquisition_date",
            "shares_sold",
            "cost_basis_per_share_usd",
            "total_cost_basis_usd",
            "total_sale_proceeds_usd",
            "gain_loss_usd",
            "commission_usd",
            "fees_usd",
            "net_proceeds_usd",
        ]
