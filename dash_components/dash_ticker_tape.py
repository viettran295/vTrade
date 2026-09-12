from dash import html
import yfinance as yf
from loguru import logger

# Symbol → Display name mapping
TICKER_SYMBOLS = {
    "^GSPC":    "S&P 500",
    "^GDAXI":   "DAX",
    "^N225":    "NIKKEI",
    "000001.SS": "SHANGHAI",
    "^HSI":     "HANG SENG",
    "^KS11":    "KOSPI",
    "GC=F":     "GOLD",
    "CL=F":     "OIL",
    "BTC-USD":  "BITCOIN",
}


class DashTickerTape:
    """Generates a scrolling ticker tape strip for the app footer."""

    @staticmethod
    def fetch_ticker_data() -> list[dict]:
        """Fetch current price and daily % change for all tracked symbols."""
        results = []
        symbols = list(TICKER_SYMBOLS.keys())

        try:
            tickers = yf.Tickers(" ".join(symbols))
            for sym in symbols:
                try:
                    ticker = tickers.tickers[sym]
                    info = ticker.fast_info
                    price = info.last_price
                    prev_close = info.previous_close

                    if price and prev_close and prev_close != 0:
                        change_pct = ((price - prev_close) / prev_close) * 100
                    else:
                        change_pct = 0.0

                    results.append({
                        "symbol": TICKER_SYMBOLS[sym],
                        "price": price if price else 0,
                        "change_pct": change_pct,
                    })
                except Exception as e:
                    logger.warning(f"Ticker {sym} fetch failed: {e}")
                    results.append({
                        "symbol": TICKER_SYMBOLS[sym],
                        "price": 0,
                        "change_pct": 0,
                    })
        except Exception as e:
            logger.error(f"Bulk ticker fetch failed: {e}")
            for sym in symbols:
                results.append({
                    "symbol": TICKER_SYMBOLS[sym],
                    "price": 0,
                    "change_pct": 0,
                })

        return results

    @staticmethod
    def build_ticker_children(data: list[dict]) -> list:
        """Build the Dash HTML children for the ticker strip from data."""
        items = []
        for entry in data:
            price = entry["price"]
            change = entry["change_pct"]

            # Format price: large numbers without decimals, small with 2
            if price >= 1000:
                price_str = f"{price:,.0f}"
            elif price >= 1:
                price_str = f"{price:,.2f}"
            else:
                price_str = f"{price:.4f}"

            # Format change
            arrow = "▲" if change >= 0 else "▼"
            change_class = "tick-up" if change >= 0 else "tick-dn"

            items.append(
                html.Span(
                    className="ticker-item",
                    children=[
                        html.Span(entry["symbol"], className="tick-sym"),
                        html.Span(" "),
                        html.Span(price_str, className="tick-val"),
                        html.Span(" "),
                        html.Span(
                            f"{arrow} {abs(change):.2f}%",
                            className=change_class,
                        ),
                    ],
                )
            )

        set_a = html.Div(className="ticker-scroll-set", children=items)
        set_b = html.Div(className="ticker-scroll-set", children=items)
        return [
            html.Div(className="ticker-scroll-inner", children=[set_a, set_b])
        ]

    @staticmethod
    def layout():
        """Return the ticker tape footer layout (initially empty, populated by callback)."""
        return html.Div(
            id="ticker-tape-footer",
            className="ticker-tape-footer",
            children=[
                html.Div(
                    className="ticker-scroll-inner",
                    children=[
                        html.Span("Loading market data...", className="tick-sym")
                    ],
                )
            ],
        )
