from playwright.sync_api import expect

from .common import *

def test_fundamental_balance_sheet_graph(page, app_url):
    """
    Test end to end fundamental balance sheet graph
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
    expect(page.locator("rect").nth(4)).to_be_visible()

def test_fundamental_cash_flow_graph(page, app_url):
    """
    Test end to end fundamental cash flow graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("COIN")
    page.get_by_role("button", name="Search").click()
    # Click Fundamental tab and verify the graph exists
    page.locator("#fa-id").click()
    expect(page.locator("#fa-id")).to_be_visible()
    expect(page.get_by_text("Fundamental Analysis")).to_be_visible()
    cash_flow_graph = page.locator("#cash-flow-graph")
    expect(cash_flow_graph).to_be_visible()
    cash_flow_graph.scroll_into_view_if_needed()
    expect(page.locator("#cash-flow-graph > .js-plotly-plot > .plot-container > .user-select-none > svg > .draglayer > .xy > .nsewdrag")).to_be_visible()