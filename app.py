from dash import Dash, html, callback, Input, Output, State, dcc, ctx
import dash
import dash_bootstrap_components as dbc
from dash_components import RegisterCallbacks, DashTickerTape
from dotenv import load_dotenv
import asyncio
from loguru import logger
from datetime import datetime

from fundamental import FinancialStatement
from common import FUNDAMENTAL_DATA_CACHE_ID
from utils.comm_interface import HttpComm

load_dotenv()

app = Dash(
    title="Trust the Algorithms",
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME],
)
server = app.server
app._favicon = "bull_icon.ico"

rc = RegisterCallbacks()
ticker_tape = DashTickerTape()

def _above_header():
    """Date time at the very top."""
    return html.Div(id="fn-datetime", className="bbg-fnbar")


def _header():
    """Header: bull icon + title."""
    return html.Div([
        html.Img(src="assets/bull_icon.png", className="bbg-bull-icon"),
        html.H1("TRUST THE ALGORITHMS"),
    ], className="bbg-header")


app.layout = html.Div(
    className="bbg-layout",
    children=[
        # ── Function-key bar ─────────────────────────────────
        _above_header(),
        dcc.Interval(id="interval-datetime", interval=60000),

        # ── Header ───────────────────────────────────────────
        _header(),

        # ── Main content (sidebar + tabs) ────────────────────
        html.Div(
            className="bbg-main-content",
            children=[
                # Column 1: Controls Sidebar (width=2)
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    # Section: search
                                    html.Div([
                                        html.Div("▶ SECURITY SEARCH", className="bbg-section-label"),
                                        html.Div([
                                            dbc.Input(
                                                id="search-stock",
                                                type="text",
                                                placeholder="Stock symbol",
                                                className="mb-2 w-100",
                                            ),
                                            dbc.Button(
                                                id="search-button",
                                                children="Search",
                                                n_clicks=0,
                                                color="success",
                                                className="w-100",
                                            ),
                                        ]),
                                    ], className="bbg-sidebar-section"),

                                    # Section: indicators checklist
                                    rc.checklist.layout(),
                                ],
                                className="bbg-sidebar-body",
                            ),
                            className="bbg-sidebar-card",
                        )
                    ],
                    width=2,
                    className="bbg-sidebar",
                ),

                # Column 2: Center Interactive Chart Panel (width=6)
                dbc.Col(
                    [
                        rc.x_ma.layout(),
                        rc.dash_bb.layout(),
                        rc.dash_rsi.layout(),
                    ],
                    className="bbg-center-panel",
                    width=8,
                ),

                # Column 3: Right Fundamental Analysis Intelligence Panel (width=4)
                dbc.Col(
                    [
                        rc.fa.layout(),
                        html.Div(
                            [
                                rc.dash_balance_sheet.layout(),
                                rc.dash_income_statement.layout(),
                                rc.dash_financial_ratios.layout(),
                            ],
                            style={"display": "none"},
                        ),
                    ],
                    className="bbg-right-panel",
                    width=2,
                ),
            ],
        ),
        # ── Footer ticker tape ────────────────────────────────
        ticker_tape.layout(),
        dcc.Interval(id="interval-ticker-tape-footer", interval=60 * 60 * 1000),

        # Stores
        dcc.Store(id="activate-search"),
        dcc.Store(id=FUNDAMENTAL_DATA_CACHE_ID),
    ],
)


@callback(
    Output("activate-search", "data"),
    Input("search-button", "n_clicks"),
    State("search-stock", "value"),
)
def update_stock_data(_, search_stock):
    if "search-button" == ctx.triggered_id:
        return search_stock
    return dash.no_update


@callback(
    Output("fn-datetime", "children"),
    Input("interval-datetime", "n_intervals"),
)
def update_datetime(_):
    now = datetime.now().strftime("%a %d %b %Y  %H:%M").upper()
    return now


@callback(
    Output("ticker-tape-footer", "children"),
    Input("interval-ticker-tape-footer", "n_intervals"),
)
def update_ticker_tape(_):
    data = ticker_tape.fetch_ticker_data()
    return ticker_tape.build_ticker_children(data)


@callback(
    Output(FUNDAMENTAL_DATA_CACHE_ID, "data"),
    Input("activate-search", "data"),
    State("search-stock", "value"),
    prevent_initial_call=True,
)
def fetch_fundamental_data(_, search_stock):
    if search_stock:
        try:
            logger.debug("Fetch financial statement and industry ratios")
            fs = FinancialStatement()
            fs._data_fetcher = HttpComm

            async def _fetch_all():
                history_coro = fs.fetch_financial_statement(search_stock)
                ratios_coro = fs.fetch_industry_ratios(search_stock)
                return await asyncio.gather(history_coro, ratios_coro, return_exceptions=True)

            history_data, ratios_data = asyncio.run(_fetch_all())

            payload = {}
            if isinstance(history_data, dict):
                payload.update(history_data)
            if isinstance(ratios_data, dict):
                payload["industry_ratios"] = ratios_data

            return payload if payload else None
        except Exception as e:
            logger.error(f"Error fetching fundamental data: {e}")
            return None


rc.register_MA_plot_callbacks()
rc.register_RSI_plot_callback()
rc.register_BB_plot_callback()
rc.register_best_performance_MA()
rc.register_best_performance_RSI()
rc.register_best_performance_BB()
rc.register_fundamental_analysis_callbacks()
rc.register_fundamental_balance_sheet()
rc.register_fundamental_income_statement()
rc.register_fundamental_ratios()

if __name__ == "__main__":
    app.run(debug=True)
