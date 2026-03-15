# AGENTS.md

## Purpose

This repo extracts Morgan Stanley at Work / Solium stock sale data from saved HTML pages and exports either CSV or an accountant-style `.xlsx` workbook.

The current source of truth is saved transaction HTML, not PDF. PDF support was intentionally removed because HTML preserves wash-sale tooltip data such as original acquisition date and original cost basis.

## Stack

- Python managed with `uv`
- CLI entrypoint: `uv run rsu-extract extract`
- HTML parsing: `beautifulsoup4`
- Workbook export: `openpyxl`
- Tests: `pytest`

## Supported Inputs

- Single saved sale HTML file: `.html` or `.htm`
- Folder of saved sale HTML files

Do not reintroduce PDF parsing unless explicitly requested. The HTML path is more reliable and contains `H` tooltip data needed for tax work.

## Output Modes

- `.csv`: one row per acquisition lot sold
- `.xlsx`: accountant-style workbook with:
  - `Sales Breakdown`
  - `Transaction Breakdown`

## Important Data Rules

- For `H` wash-sale rows, use the tooltip values:
  - `Original acquisition date`
  - `Original cost basis per share`
- For non-`H` rows, use the visible row values.
- Keep transaction-level fees and net proceeds at the transaction level.
- `Transaction Breakdown` must stay aligned with the accountant format:
  - `Transaction Date`
  - `Shares Sold`
  - `Price Per Share`
  - `Gross Proceeds USD`
  - `Fees USD`
  - `Net Proceeds USD`
  - `Currency`
  - `Converted Net Proceeds`

## Common Commands

```bash
uv sync
uv run pytest
uv run rsu-extract extract --input "/path/to/html-or-folder" --output stock-sales.xlsx
```

## Implementation Notes

- Prefer extending `src/rsu_extract/parser_html.py` instead of creating parallel parsers.
- Preserve the current workbook styling and grouping unless a task explicitly asks to change presentation.
- When changing extraction logic, add or update tests in `tests/test_parser_html.py` and `tests/test_exporters.py`.
