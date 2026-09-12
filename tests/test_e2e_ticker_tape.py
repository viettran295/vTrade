import re
from playwright.sync_api import expect

from .common import *


def test_ticker_tape_is_visible(page, app_url):
    """The ticker tape footer should be visible on initial page load."""
    page.goto(app_url)
    footer = page.locator("#ticker-tape-footer")
    expect(footer).to_be_visible()


def test_ticker_tape_contains_market_symbols(page, app_url):
    """After data loads, the tape should display all expected market symbols."""
    expected_symbols = [
        "S&P 500", "DAX", "NIKKEI", "SHANGHAI",
        "HANG SENG", "KOSPI", "GOLD", "OIL", "BITCOIN",
    ]
    page.goto(app_url)
    footer = page.locator("#ticker-tape-footer")
    expect(footer).to_be_visible()

    # Wait for market data to replace the "Loading..." placeholder
    page.locator("#ticker-tape-footer .ticker-item").first.wait_for(
        state="visible", timeout=60_000
    )

    footer_text = footer.inner_text()
    for sym in expected_symbols:
        assert sym in footer_text, f"Expected '{sym}' in ticker tape, got: {footer_text}"


def test_ticker_tape_shows_prices_and_percent_changes(page, app_url):
    """Each ticker item should contain a price number and a percent change."""
    page.goto(app_url)
    page.locator("#ticker-tape-footer .ticker-item").first.wait_for(
        state="visible", timeout=30_000
    )

    items = page.locator("#ticker-tape-footer .ticker-item")
    count = items.count()
    assert count >= 9, f"Expected at least 9 ticker items, got {count}"

    for i in range(min(9, count)):
        item = items.nth(i)
        # Check price value exists
        tick_val = item.locator(".tick-val")
        expect(tick_val).to_be_visible()
        price_text = tick_val.inner_text()
        assert re.search(r"\d", price_text), f"No digits in price: {price_text}"

        # Check percent change exists (▲ or ▼ followed by a number%)
        change_el = item.locator(".tick-up, .tick-dn")
        expect(change_el).to_be_visible()
        change_text = change_el.inner_text()
        assert re.search(r"[▲▼]\s*\d+\.\d+%", change_text), (
            f"Unexpected change format: {change_text}"
        )


def test_ticker_tape_scroll_animation_is_running(page, app_url):
    """The ticker-scroll-inner should have an active CSS animation."""
    page.goto(app_url)
    page.locator("#ticker-tape-footer .ticker-item").first.wait_for(
        state="visible", timeout=30_000
    )

    inner = page.locator("#ticker-tape-footer .ticker-scroll-inner")
    animation_name = inner.evaluate(
        "el => getComputedStyle(el).animationName"
    )
    assert animation_name == "ticker-scroll", (
        f"Expected animation 'ticker-scroll', got '{animation_name}'"
    )

    play_state = inner.evaluate(
        "el => getComputedStyle(el).animationPlayState"
    )
    assert play_state == "running", (
        f"Expected animation to be running, got '{play_state}'"
    )
