from playwright.sync_api import expect

from .common import *


def test_fundamental_analysis(page, app_url):
    """
    Test end to end SEC Fundamental Intelligence panel:
    - Side-by-side Liquidity Ratios (Current/Quick)
    - Debt-to-Equity Gauge vs Peer Median
    - Quarterly Revenue Bars
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("TSLA")
    page.get_by_role("button", name="Search").click()

    # Verify Fundamental Analysis panel elements are visible
    expect(page.get_by_text("SEC FUNDAMENTAL INTELLIGENCE")).to_be_visible()
    expect(page.get_by_text("CURRENT RATIO")).to_be_visible()
    expect(page.get_by_text("QUICK RATIO")).to_be_visible()
    expect(page.get_by_text("DEBT-TO-EQUITY VS PEER MEDIAN")).to_be_visible()
    expect(page.get_by_text("QUARTERLY REVENUE BARS")).to_be_visible()

    gauge_graph = page.locator("#sec-debt-equity-gauge")
    expect(gauge_graph).to_be_visible()

    revenue_graph = page.locator("#sec-quarterly-revenue-graph")
    expect(revenue_graph).to_be_visible()
