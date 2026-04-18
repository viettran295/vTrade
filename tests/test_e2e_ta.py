from playwright.sync_api import expect

from .common import *

def test_crossing_ma_graph(page, app_url):
    """
    Test end to end Crossing MA graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("COIN")
    page.get_by_role("button", name="Search").click()
    # Verify the crossing MA graph exists
    expect(page.get_by_text("Crossing MA")).to_be_visible()
    expect(page.get_by_role("checkbox", name="Crossing MA")).to_be_visible()
    expect(page.get_by_text("Short moving average")).to_be_visible()
    expect(page.locator("#short-ma-input")).to_be_visible()
    expect(page.get_by_text("Long moving average")).to_be_visible()
    expect(page.locator("#long-ma-input")).to_be_visible()
    expect(page.get_by_text("SMA", exact=True)).to_be_visible()
    expect(page.get_by_role("radio", name="SMA")).to_be_visible()
    expect(page.get_by_text("EWMA")).to_be_visible()
    expect(page.get_by_role("radio", name="EWMA")).to_be_visible()
    expect(page.get_by_role("button", name="Apply")).to_be_visible()
    expect(page.locator("rect").nth(4)).to_be_visible()
    expect(page.locator(".bg")).to_be_visible()

def test_bollingerbands_graph(page, app_url):
    """
    Test end to end Bollinger bands graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("NVDA")
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_text("Bollinger bands")).to_be_visible()
    expect(page.get_by_role("checkbox", name="Bollinger bands")).to_be_visible()
    page.get_by_role("checkbox", name="Bollinger bands").check()
    # Verify the Bollinger bands graph exists
    bb_graph = page.locator("#bb-graph")
    expect(bb_graph).to_be_visible()
    bb_graph.scroll_into_view_if_needed()
    expect(page.locator("#bb-graph > .js-plotly-plot > .plot-container > .user-select-none > svg > .draglayer > .xy > .nsewdrag")).to_be_visible()

def test_rsi_graph(page, app_url):
    """
    Test end to end fundamental graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("GOOG")
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_text("RSI")).to_be_visible()
    expect(page.get_by_role("checkbox", name="RSI")).to_be_visible()
    page.get_by_role("checkbox", name="RSI").check()
    # Verify the Bollinger bands graph exists
    rsi_graph = page.locator("#rsi-graph")
    expect(rsi_graph).to_be_visible()
    rsi_graph.scroll_into_view_if_needed()
    expect(page.locator("#rsi-graph > .js-plotly-plot > .plot-container > .user-select-none > svg > .draglayer > .xy > .nsewdrag")).to_be_visible()
