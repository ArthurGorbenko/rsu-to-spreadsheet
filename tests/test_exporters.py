from datetime import datetime
from decimal import Decimal
from pathlib import Path

from openpyxl import load_workbook

from rsu_extract.exporters import write_xlsx
from rsu_extract.models import SaleLotRow


def test_write_xlsx_groups_transactions_and_writes_formulas(tmp_path: Path) -> None:
    output = tmp_path / "report.xlsx"
    rows = [
        SaleLotRow(
            transaction_id="TXN1",
            sale_date="December 16, 2025",
            settlement_date="December 17, 2025",
            sale_price_usd=Decimal("10.92"),
            acquisition_date="December 20, 2024",
            shares_sold=Decimal("50"),
            cost_basis_per_share_usd=Decimal("18.86"),
            total_cost_basis_usd=Decimal("943.00"),
            total_sale_proceeds_usd=Decimal("546.00"),
            gain_loss_usd=Decimal("-396.72"),
            commission_usd=None,
            fees_usd=None,
            net_proceeds_usd=None,
            proceeds_currency="USD",
            converted_net_proceeds=None,
        ),
        SaleLotRow(
            transaction_id="TXN1",
            sale_date="December 16, 2025",
            settlement_date="December 17, 2025",
            sale_price_usd=Decimal("10.92"),
            acquisition_date="February 20, 2025",
            shares_sold=Decimal("120"),
            cost_basis_per_share_usd=Decimal("11.93"),
            total_cost_basis_usd=Decimal("1431.60"),
            total_sale_proceeds_usd=Decimal("1310.40"),
            gain_loss_usd=Decimal("-120.67"),
            commission_usd=None,
            fees_usd=None,
            net_proceeds_usd=None,
            proceeds_currency="USD",
            converted_net_proceeds=None,
        ),
        SaleLotRow(
            transaction_id="TXN2",
            sale_date="June 9, 2025",
            settlement_date="June 10, 2025",
            sale_price_usd=Decimal("10.36"),
            acquisition_date="",
            shares_sold=Decimal("100"),
            cost_basis_per_share_usd=Decimal("6.60"),
            total_cost_basis_usd=Decimal("660.00"),
            total_sale_proceeds_usd=Decimal("1036.00"),
            gain_loss_usd=Decimal("376.00"),
            commission_usd=Decimal("9.95"),
            fees_usd=Decimal("10.00"),
            net_proceeds_usd=Decimal("1016.05"),
            proceeds_currency="CAD",
            converted_net_proceeds=Decimal("1349.73"),
        ),
    ]

    write_xlsx(output, rows)

    workbook = load_workbook(output, data_only=False)
    sales_sheet = workbook["Sales Breakdown"]
    transactions_sheet = workbook["Transaction Breakdown"]

    assert sales_sheet["A1"].value == "June 9, 2025"
    assert sales_sheet["A2"].value == "Acquisition Date"
    assert sales_sheet["E3"].value == "=B3*C3"
    assert sales_sheet["F3"].value == "=B3*D3"
    assert sales_sheet["G4"].value == "=F4-E4"

    assert transactions_sheet["A1"].value == "Transaction Date"
    assert transactions_sheet["A2"].value == datetime(2025, 6, 9)
    assert transactions_sheet["A2"].number_format == "yyyy-mm-dd"
    assert transactions_sheet["E2"].value == 19.95
    assert transactions_sheet["F2"].value == 1016.05
    assert transactions_sheet["G2"].value == "CAD"
    assert transactions_sheet["H2"].value == 1349.73
    assert transactions_sheet["A3"].value == datetime(2025, 12, 16)
    assert transactions_sheet["F3"].value == "=D3-E3"
    assert sales_sheet["A12"].value == "Overall Totals"
    assert sales_sheet["A13"].value == "Total Shares Sold"
    assert sales_sheet["A14"].value == "=B3+B8+B9"
    assert sales_sheet["B14"].value == "=E3+E8+E9"
    assert sales_sheet["C14"].value == "=F3+F8+F9"
    assert sales_sheet["D14"].value == "=G3+G8+G9"
