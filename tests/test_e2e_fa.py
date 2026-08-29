from playwright.sync_api import expect

from .common import *


def test_fundamental_balance_sheet_graph(page, app_url):
    """
    Test end to end fundamental balance sheet & cash flow merged graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("TSLA")
    page.get_by_role("button", name="Search").click()
    # Click Fundamental tab and verify the graph exists
    page.locator("#fa-id").click()
    expect(page.locator("#fa-id")).to_be_visible()
    expect(page.get_by_text("Fundamental Analysis")).to_be_visible()
    bs_graph = page.locator("#balance-sheet-graph")
    expect(bs_graph).to_be_visible()
    bs_graph.scroll_into_view_if_needed()
    expect(
        page.locator(
            "#balance-sheet-graph > .js-plotly-plot > .plot-container > .user-select-none > svg > .draglayer > .xy > .nsewdrag"
        )
    ).to_be_visible()


def test_fundamental_income_statement_graph(page, app_url):
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("AMD")
    page.get_by_role("button", name="Search").click()
    # Click Fundamental tab and verify the graph exists
    page.locator("#fa-id").click()
    expect(page.locator("#fa-id")).to_be_visible()
    expect(page.get_by_text("Fundamental Analysis")).to_be_visible()
    page.get_by_role("button", name="Search").click()
    page.locator("#fa-id").click()
    expect(
        page.locator(
            "#income-statement-graph > .js-plotly-plot > .plot-container > .user-select-none > svg > .draglayer > .xy > .nsewdrag"
        )
    ).to_be_visible()

def test_fundamental_ratios_graph(page, app_url):
    """
    Test end to end fundamental financial ratios graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("TSLA")
    page.get_by_role("button", name="Search").click()
    # Click Fundamental tab and verify the financial ratios graph exists
    page.locator("#fa-id").click()
    expect(page.locator("#fa-id")).to_be_visible()
    expect(page.get_by_text("Fundamental Analysis")).to_be_visible()
    ratios_graph = page.locator("#financial-ratios-graph")
    expect(ratios_graph).to_be_visible()
    ratios_graph.scroll_into_view_if_needed()
    expect(
        page.locator(
            "#financial-ratios-graph > .js-plotly-plot > .plot-container > .user-select-none > svg > .draglayer > .xy > .nsewdrag"
        )
    ).to_be_visible()
