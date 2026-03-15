from decimal import Decimal

from rsu_extract.parser_html import parse_html_text


def test_parse_html_uses_original_basis_from_h_tooltip() -> None:
    html = """
    <html><body>
      <div><div aria-label="title"><span>Date entered</span></div><div aria-label="content"><span>May 22, 2025</span></div></div>
      <div><div aria-label="title"><span>Reference number</span></div><div aria-label="content">WRCCEDF6C76-1EE</div></div>
      <div><div aria-label="title"><span>Settlement date</span></div><div aria-label="content"><span>May 23, 2025</span></div></div>
      <div><div aria-label="title"><span>Proceeds currency</span></div><div aria-label="content">USD</div></div>
      <div><div aria-label="title"><span>Value per share</span></div><div aria-label="content"><span>$11.08</span></div></div>
      <div class="breakdownRow-container"><span>Proceeds</span><span class="breakdownRow-right">$1,000.00</span></div>
      <div class="breakdownRow-container"><span>Wire Fee</span><span class="breakdownRow-right">- $25.00</span></div>
      <div class="breakdownRow-container"><span>Brokerage Commission</span><span class="breakdownRow-right">- $9.95</span></div>
      <div class="breakdownRow-container"><span>Estimated Net Proceeds</span><span class="breakdownRow-right">$965.05</span></div>
      <h5><span>Fill summary</span></h5>
      <div class="breakdownRow-container"><span>Sale price</span><span class="breakdownRow-right">$10.00</span></div>
      <div class="breakdownRow-container"><span>Quantity Filled</span><span class="breakdownRow-right">100</span></div>
      <h5><span>Fill details</span></h5>
      <div><span>May 22, 2025</span></div>
      <table>
        <caption>Summary of shares sold with a short term gain or loss.</caption>
        <tbody>
          <tr>
            <td><span>March 6, 2025</span></td><td></td><td><span>$11.65</span></td><td><span>$10.00</span></td><td><span>56.001</span></td><td><span>−$92.39</span></td>
            <td>
              <button aria-label="Toggle wash sale indicator to show original acquisition information"><span>H</span></button>
              <div><div aria-label="title"><span>Original acquisition date</span></div><div aria-label="content"><span>March 20, 2025</span></div></div>
              <div><div aria-label="title"><span>Original cost basis per share</span></div><div aria-label="content"><span>$9.85</span></div></div>
            </td>
          </tr>
        </tbody>
      </table>
    </body></html>
    """

    rows = parse_html_text(html)

    assert len(rows) == 1
    row = rows[0]
    assert row.transaction_id == "WRCCEDF6C76-1EE"
    assert row.sale_date == "May 22, 2025"
    assert row.settlement_date == "May 23, 2025"
    assert row.acquisition_date == "March 20, 2025"
    assert row.cost_basis_per_share_usd == Decimal("9.85")
    assert row.total_cost_basis_usd == Decimal("551.61")
    assert row.total_sale_proceeds_usd == Decimal("1000.00")
    assert row.gain_loss_usd == Decimal("8.40")
    assert row.commission_usd == Decimal("9.95")
    assert row.fees_usd == Decimal("25.00")
    assert row.net_proceeds_usd == Decimal("965.05")
