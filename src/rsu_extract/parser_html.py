from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from bs4 import BeautifulSoup

from rsu_extract.models import SaleLotRow


def parse_html(path: Path) -> list[SaleLotRow]:
    return parse_html_text(path.read_text(encoding="utf-8", errors="ignore"))


def parse_html_text(html: str) -> list[SaleLotRow]:
    soup = BeautifulSoup(html, "html.parser")

    transaction_id = _extract_labeled_value(soup, "Reference number") or ""
    settlement_date = _extract_labeled_value(soup, "Settlement date") or ""
    sale_date = _extract_fill_date(soup) or _extract_labeled_value(soup, "Date entered") or ""
    sale_price = _parse_money(_find_breakdown_value(soup, "Sale price") or _find_breakdown_value(soup, "Market Price per Unit"))
    total_proceeds = _parse_money(_find_breakdown_value(soup, "Proceeds"))
    commission = _abs_money(_parse_money(_find_breakdown_value(soup, "Brokerage Commission")))
    fees = _sum_optional(
        _abs_money(_parse_money(_find_breakdown_value(soup, "Wire Fee"))),
        _abs_money(_parse_money(_find_breakdown_value(soup, "International ACH"))),
        _abs_money(_parse_money(_find_breakdown_value(soup, "Supplemental Transaction Fee"))),
    )
    net_proceeds = _parse_money(
        _find_breakdown_value(soup, "Estimated Net Proceeds") or _find_breakdown_value(soup, "Net Proceeds")
    )
    proceeds_currency = _extract_labeled_value(soup, "Proceeds currency") or "USD"
    converted_net_proceeds = _parse_money(_find_breakdown_value(soup, "Converted Net Proceeds"))

    rows = _extract_cost_basis_rows(
        soup=soup,
        transaction_id=transaction_id,
        sale_date=sale_date,
        settlement_date=settlement_date,
        sale_price=sale_price,
        total_proceeds=total_proceeds,
        commission=commission,
        fees=fees,
        net_proceeds=net_proceeds,
        proceeds_currency=proceeds_currency,
        converted_net_proceeds=converted_net_proceeds,
    )
    if rows:
        return rows

    espp_row = _extract_espp_row(
        soup=soup,
        transaction_id=transaction_id,
        sale_date=sale_date,
        settlement_date=settlement_date,
        sale_price=sale_price,
        total_proceeds=total_proceeds,
        commission=commission,
        fees=fees,
        net_proceeds=net_proceeds,
        proceeds_currency=proceeds_currency,
        converted_net_proceeds=converted_net_proceeds,
    )
    if espp_row is None:
        raise ValueError("No sale rows found in HTML.")
    return [espp_row]


def _extract_cost_basis_rows(
    *,
    soup: BeautifulSoup,
    transaction_id: str,
    sale_date: str,
    settlement_date: str,
    sale_price: Decimal | None,
    total_proceeds: Decimal | None,
    commission: Decimal | None,
    fees: Decimal | None,
    net_proceeds: Decimal | None,
    proceeds_currency: str,
    converted_net_proceeds: Decimal | None,
) -> list[SaleLotRow]:
    rows: list[SaleLotRow] = []
    table = soup.find("caption", string=re.compile("Summary of shares sold", re.I))
    if table is None:
        return rows

    tbody = table.find_parent("table")
    if tbody is None:
        return rows

    tr_nodes = tbody.find("tbody")
    if tr_nodes is None:
        return rows

    for tr in tr_nodes.find_all("tr", recursive=False):
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 6:
            continue
        acquisition_date = _extract_date_text(tds[0].get_text(" ", strip=True))
        cost_basis = _parse_money(tds[2].get_text(" ", strip=True))
        shares = _parse_decimal(tds[4].get_text(" ", strip=True))
        reported_gain_loss = _parse_money(tds[5].get_text(" ", strip=True))
        original_acq = _extract_date_text(_extract_nested_label_value(tds[-1], "Original acquisition date") or "")
        original_basis = _parse_money(_extract_nested_label_value(tds[-1], "Original cost basis per share"))
        effective_acq = original_acq or acquisition_date
        effective_basis = original_basis if original_basis is not None else cost_basis
        total_cost = _multiply_money(effective_basis, shares)
        total_sale = _multiply_money(sale_price, shares)
        gain_loss = _subtract_money(total_sale, total_cost) if original_basis is not None else reported_gain_loss
        rows.append(
            SaleLotRow(
                transaction_id=transaction_id,
                sale_date=sale_date,
                settlement_date=settlement_date,
                sale_price_usd=sale_price,
                acquisition_date=effective_acq,
                shares_sold=shares,
                cost_basis_per_share_usd=effective_basis,
                total_cost_basis_usd=total_cost,
                total_sale_proceeds_usd=total_sale,
                gain_loss_usd=gain_loss,
                commission_usd=None,
                fees_usd=None,
                net_proceeds_usd=None,
                proceeds_currency=proceeds_currency,
                converted_net_proceeds=None,
            )
        )

    if rows:
        row = rows[0]
        if len(rows) == 1 and row.total_sale_proceeds_usd is not None:
            row.total_sale_proceeds_usd = total_proceeds or row.total_sale_proceeds_usd
        row.commission_usd = commission
        row.fees_usd = fees
        row.net_proceeds_usd = net_proceeds
        row.converted_net_proceeds = converted_net_proceeds
    return rows


def _extract_espp_row(
    *,
    soup: BeautifulSoup,
    transaction_id: str,
    sale_date: str,
    settlement_date: str,
    sale_price: Decimal | None,
    total_proceeds: Decimal | None,
    commission: Decimal | None,
    fees: Decimal | None,
    net_proceeds: Decimal | None,
    proceeds_currency: str,
    converted_net_proceeds: Decimal | None,
) -> SaleLotRow | None:
    shares = _parse_decimal(_find_breakdown_value(soup, "Quantity Filled") or _find_breakdown_value(soup, "Shares To Be Sold"))
    cost_basis = _parse_money(_extract_labeled_value(soup, "Value per share"))
    if shares is None or cost_basis is None:
        return None
    gain_loss = _sum_optional(
        _parse_money(_find_breakdown_value(soup, "Ordinary Income")),
        _parse_money(_find_breakdown_value(soup, "Capital Gain or Loss")),
    )
    return SaleLotRow(
        transaction_id=transaction_id,
        sale_date=sale_date,
        settlement_date=settlement_date,
        sale_price_usd=sale_price,
        acquisition_date="",
        shares_sold=shares,
        cost_basis_per_share_usd=cost_basis,
        total_cost_basis_usd=_multiply_money(cost_basis, shares),
        total_sale_proceeds_usd=total_proceeds,
        gain_loss_usd=gain_loss,
        commission_usd=commission,
        fees_usd=fees,
        net_proceeds_usd=net_proceeds,
        proceeds_currency=proceeds_currency,
        converted_net_proceeds=converted_net_proceeds,
    )


def _extract_labeled_value(soup: BeautifulSoup, label: str) -> str | None:
    title = soup.find(attrs={"aria-label": "title"}, string=re.compile(rf"^\s*{re.escape(label)}\s*$", re.I))
    if title is None:
        title = soup.find(lambda tag: tag.name in {"div", "span"} and _clean_text(tag.get_text(" ", strip=True)) == label)
        if title is None:
            return None
        parent = title.parent
        if parent is None:
            return None
        content = parent.find(attrs={"aria-label": "content"})
        return _clean_text(content.get_text(" ", strip=True)) if content else None
    parent = title.parent
    if parent is None:
        return None
    content = parent.find(attrs={"aria-label": "content"})
    return _clean_text(content.get_text(" ", strip=True)) if content else None


def _find_breakdown_value(soup: BeautifulSoup, label: str) -> str | None:
    for container in soup.find_all(class_=re.compile("breakdownRow-container")):
        text_nodes = [node for node in container.find_all(["span", "div"], recursive=False)]
        if len(text_nodes) >= 2:
            left = _clean_text(text_nodes[0].get_text(" ", strip=True))
            right = _clean_text(text_nodes[-1].get_text(" ", strip=True))
            if left == label and right:
                return right

        left_candidates = container.find_all(class_=re.compile("breakdownRow-left"))
        right_candidates = container.find_all(class_=re.compile("breakdownRow-right"))
        if left_candidates and right_candidates:
            left = _clean_text(left_candidates[0].get_text(" ", strip=True))
            right = _clean_text(right_candidates[0].get_text(" ", strip=True))
            if left == label and right:
                return right

    for span in soup.find_all("span"):
        if _clean_text(span.get_text(" ", strip=True)) != label:
            continue
        container = span.find_parent(class_=re.compile("breakdownRow-container"))
        if container is None:
            continue
        right = container.find(class_=re.compile("breakdownRow-right"))
        if right is None:
            continue
        return _clean_text(right.get_text(" ", strip=True))
    return None


def _extract_nested_label_value(node, label: str) -> str | None:
    title = node.find(attrs={"aria-label": "title"}, string=re.compile(rf"^\s*{re.escape(label)}\s*$", re.I))
    if title is None:
        return None
    parent = title.parent
    if parent is None:
        return None
    content = parent.find(attrs={"aria-label": "content"})
    return _clean_text(content.get_text(" ", strip=True)) if content else None


def _extract_fill_date(soup: BeautifulSoup) -> str | None:
    fill_header = soup.find("h5", string=re.compile(r"Fill details", re.I))
    if fill_header is None:
        return None
    container = fill_header.find_parent()
    if container is None:
        return None
    match = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", container.parent.get_text(" ", strip=True))
    return match.group(1) if match else None


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def _extract_date_text(value: str) -> str:
    cleaned = _clean_text(value)
    match = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", cleaned)
    return match.group(1) if match else cleaned


def _parse_money(value: str | None) -> Decimal | None:
    if not value:
        return None
    cleaned = value
    cleaned = cleaned.replace("CA$", "").replace("$", "").replace(",", "")
    cleaned = cleaned.replace("−", "-").replace("&nbsp;", "").replace(" ", "")
    cleaned = cleaned.replace("×", "")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return Decimal(match.group(0)) if match else None


def _parse_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    match = re.search(r"\d+(?:\.\d+)?", value.replace(",", ""))
    return Decimal(match.group(0)) if match else None


def _multiply_money(left: Decimal | None, right: Decimal | None) -> Decimal | None:
    if left is None or right is None:
        return None
    return (left * right).quantize(Decimal("0.01"))


def _subtract_money(left: Decimal | None, right: Decimal | None) -> Decimal | None:
    if left is None or right is None:
        return None
    return (left - right).quantize(Decimal("0.01"))


def _sum_optional(*values: Decimal | None) -> Decimal | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(present, Decimal("0")).quantize(Decimal("0.01"))


def _abs_money(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return abs(value)
