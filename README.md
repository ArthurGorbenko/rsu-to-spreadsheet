# rsu-extract

CLI tool to extract Morgan Stanley at Work / Solium stock sale data from saved HTML pages into a normalized USD CSV or an accountant-style workbook.

## Setup

```bash
uv sync
```

## Usage

```bash
uv run rsu-extract extract \
  --input "/path/to/stock-sale.html" \
  --output output.csv
```

You can also point `--input` at a folder. All matching `.html` and `.htm` files are appended into one CSV or workbook.

To generate an accountant-style workbook with grouped lot sections and transaction formulas:

```bash
uv run rsu-extract extract \
  --input "/path/to/html-folder/" \
  --output stock-sales.xlsx
```

## Output Columns

- `sale_date`
- `settlement_date`
- `sale_price_usd`
- `acquisition_date`
- `shares_sold`
- `cost_basis_per_share_usd`
- `total_cost_basis_usd`
- `total_sale_proceeds_usd`
- `gain_loss_usd`
- `commission_usd`
- `fees_usd`
- `net_proceeds_usd`

## Notes

- The CSV is one row per acquisition lot sold.
- If the output path ends in `.xlsx`, the tool writes:
  - `Sales Breakdown`: grouped by transaction date with lot rows and subtotal formulas
  - `Transaction Breakdown`: one row per transaction with fees and net proceeds at the transaction level
- This tool targets saved Morgan Stanley at Work / Solium sale HTML pages.
- HTML is the preferred source because it preserves wash-sale tooltip data such as original acquisition date and original cost basis per share.
