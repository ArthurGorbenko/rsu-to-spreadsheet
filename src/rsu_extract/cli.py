from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path
from typing import Iterable

from rsu_extract.exporters import write_xlsx
from rsu_extract.models import SaleLotRow
from rsu_extract.parser_html import parse_html


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rsu-extract")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser("extract", help="Extract sale lots into CSV.")
    extract_parser.add_argument("--input", required=True, help="HTML file or folder path.")
    extract_parser.add_argument("--output", required=True, help="Output CSV or XLSX path.")

    args = parser.parse_args(argv)
    if args.command == "extract":
        return _run_extract(Path(args.input), Path(args.output))
    return 1


def _run_extract(input_path: Path, output_path: Path) -> int:
    html_paths = list(_collect_html_paths(input_path))
    if not html_paths:
        raise SystemExit(f"No HTML files found at: {input_path}")

    rows: list[SaleLotRow] = []
    failures: list[str] = []
    for html_path in html_paths:
        try:
            rows.extend(parse_html(html_path))
        except Exception as exc:  # pragma: no cover - surfaced to CLI output
            failures.append(f"{html_path}: {exc}")

    if not rows and failures:
        raise SystemExit("Failed to parse any HTML files:\n" + "\n".join(failures))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".xlsx":
        write_xlsx(output_path, rows)
    else:
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=SaleLotRow.csv_headers())
            writer.writeheader()
            for row in rows:
                writer.writerow(_row_to_csv_dict(row))

    if failures:
        print("Completed with parse failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    return 0


def _collect_html_paths(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return
    if input_path.is_dir():
        yield from sorted(path for path in input_path.iterdir() if path.suffix.lower() in {".html", ".htm"})
        return
    raise SystemExit(f"Input path does not exist: {input_path}")


def _row_to_csv_dict(row: SaleLotRow) -> dict[str, str]:
    return {
        "sale_date": row.sale_date,
        "settlement_date": row.settlement_date,
        "sale_price_usd": _format_decimal(row.sale_price_usd),
        "acquisition_date": row.acquisition_date,
        "shares_sold": _format_decimal(row.shares_sold),
        "cost_basis_per_share_usd": _format_decimal(row.cost_basis_per_share_usd),
        "total_cost_basis_usd": _format_decimal(row.total_cost_basis_usd),
        "total_sale_proceeds_usd": _format_decimal(row.total_sale_proceeds_usd),
        "gain_loss_usd": _format_decimal(row.gain_loss_usd),
        "commission_usd": _format_decimal(row.commission_usd),
        "fees_usd": _format_decimal(row.fees_usd),
        "net_proceeds_usd": _format_decimal(row.net_proceeds_usd),
    }


def _format_decimal(value: Decimal | None) -> str:
    return "" if value is None else format(value, "f")
