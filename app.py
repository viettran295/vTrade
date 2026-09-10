from dash import Dash, html, callback, Input, Output, State, dcc, ctx
import dash
import dash_bootstrap_components as dbc
from dash_components import RegisterCallbacks
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

def _above_header():
    """Date time at the very top."""
    now = datetime.now().strftime("%a %d %b %Y  %H:%M:%S CEST").upper()
    return html.Div([html.Div(now, className="fn-datetime")], className="bbg-fnbar")


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

        # ── Header ───────────────────────────────────────────
        _header(),

        # ── Main content (sidebar + tabs) ────────────────────
        html.Div(
            className="bbg-main-content",
            children=[
                # Sidebar
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

                # Main panel
                dbc.Col(
                    [rc.tabs.layout()],
                    className="bbg-main-panel",
                    width=10,
                ),
            ],
        ),
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
rc.register_fundamental_balance_sheet()
rc.register_fundamental_income_statement()
rc.register_fundamental_ratios()

if __name__ == "__main__":
    app.run(debug=True)
