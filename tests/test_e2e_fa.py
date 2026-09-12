from playwright.sync_api import expect

from .common import *


def test_fundamental_analysis(page, app_url):
    """
    Test end to end Fundamental Analysis panel:
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("TSLA")
    page.get_by_role("button", name="Search").click()

    # Verify Fundamental Analysis panel elements are visible
    expect(page.get_by_text("■ FUNDAMENTAL ANALYSIS")).to_be_visible()
    expect(page.locator(".bbg-right-panel")).to_be_visible()
    expect(page.get_by_text("■ DEBT-TO-EQUITY VS PEER")).to_be_visible()
    expect(page.get_by_text("■ QUARTERLY REVENUE BARS")).to_be_visible()


