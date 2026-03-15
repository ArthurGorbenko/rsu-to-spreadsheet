# rsu-extract

`rsu-extract` converts saved Morgan Stanley at Work / Solium sale pages into a structured CSV or an accountant-style Excel workbook.

Morgan Stanley sale records are built for U.S. tax reporting and are painful to use for Canadian taxes. The main problem is that the broker view applies IRS-specific concepts like wash-sale adjustments, even though those rules do not apply the same way in Canada. For Canadian tax work, you often need the original lot basis rather than the adjusted U.S. number.

This project uses saved HTML pages because they preserve the hidden `H` tooltip data that the PDFs drop, including the original acquisition date and original cost basis per share.

## What It Does

Given one saved sale page or a folder of saved sale pages, the script:

- extracts transaction-level sale details
- extracts lot-level cost basis rows
- handles `H` wash-sale rows by using the original values from the HTML tooltip
- calculates lot-level totals such as:
  - total cost basis
  - total sale proceeds
  - gain or loss
- writes either:
  - a normalized CSV with one row per lot, or
  - an Excel workbook formatted for accountant review

## What The Workbook Contains

If the output ends with `.xlsx`, the script creates:

- `Sales Breakdown`
  - grouped by transaction date
  - lot rows under each transaction
  - formulas for total cost basis, total sale proceeds, and gain/loss
  - an overall totals block at the end for:
    - total shares sold
    - total cost basis
    - total sale proceeds
    - total gain/loss
- `Transaction Breakdown`
  - one row per transaction
  - transaction date
  - shares sold
  - price per share
  - gross proceeds
  - fees
  - net proceeds
  - currency
  - converted net proceeds (CAD)

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

You can also point `--input` at a folder. All matching `.html` and `.htm` files are processed and appended into one output file.

To generate the accountant workbook:

```bash
uv run rsu-extract extract \
  --input "/path/to/html-folder/" \
  --output stock-sales.xlsx
```

## Example Files

See [examples/README.md](/Users/arthur/Documents/rsu-to-spreadsheet/examples/README.md) for a synthetic saved sale page and generated example outputs.

## Output Columns

For CSV output, the script writes one row per acquisition lot with these columns:

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

## Input Expectations

- Input files should be saved Morgan Stanley at Work / Solium sale pages.
- The HTML should include the rendered transaction details page, not just a partial snippet.
- For `H` rows, the saved HTML must still contain the hidden popover content for:
  - `Original acquisition date`
  - `Original cost basis per share`

## Notes

- HTML is the preferred source because it preserves wash-sale tooltip data that matters for basis reconstruction.
- The workbook formulas are there for review and handoff, not as a substitute for professional tax advice.
- If you have both HTML and another export for the same transaction, avoid mixing them in the same run unless you want duplicate rows.
