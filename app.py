from dash import Dash, html, callback, Input, Output, State, dcc
import dash
import dash_bootstrap_components as dbc
import duckdb
import utils
import os
from dash_components import RegisterCallbacks, ConnectDB
from dotenv import load_dotenv
load_dotenv()
from loguru import logger
from strategy import vTrade
import asyncio

dbc_css = "https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/minty/bootstrap.min.css"

app = Dash(
    title="__vTrade__",
    external_stylesheets=[dbc.themes.DARKLY, dbc_css]
)

rc = RegisterCallbacks()
db_conn = ConnectDB()
db_conn.clean_up_db()

app.layout = dbc.Container(
    style = {
        "backgroundColor": utils.colors["background"],
         "height": "100vh",
    },
    children = [
        dbc.Row([
            dbc.Col([
                html.H1(
                    "vTrade App",
                    style={
                        "textAlign": "center",
                        "color": utils.colors["text"],
                    }
                ),
            ])
        ]),
        html.Br(),
        dbc.Row(
            [
                # Side Bar
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H3("Configuration"),
                                    style={
                                        "backgroundColor": utils.colors["sidebar"],
                                    }
                                ),
                                dbc.CardBody(
                                    [
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        dbc.Input(
                                                            id="search-stock",
                                                            type="text",
                                                            placeholder="Stock symbol",
                                                            className="mb-3 mr-3 ml-1 w-50"
                                                        ),
                                                        dbc.Button(
                                                            id="search-button",
                                                            children="Search",
                                                            target="blank",
                                                            n_clicks=0,
                                                            color="success",
                                                            className="mb-3"
                                                        ),
                                                    ],
                                                    style={
                                                        "display": "flex"
                                                    }
                                                ),
                                                rc.checklist.layout()
                                            ]
                                        )
                                    ],
                                    style={
                                        "display": "flex",
                                        "backgroundColor": utils.colors["sidebar"],
                                        "padding-left": "0px"
                                    }
                                ),
                            ], 
                        )
                    ],
                    width=2
                ),
                # Main Content
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    tab_id="ta_tab",
                                    label="Technical Analysis",
                                    children=[
                                        html.Br(),
                                        rc.x_ma.layout(),
                                    ],
                                    active_tab_style={
                                        "fontStyle": "italic",
                                    },
                                    active_label_style={
                                        "color": "#000000",
                                    },
                                    style={"marginBottom": "20px"},
                                ),
                                dbc.Tab(
                                    tab_id="bt-tab",
                                    label="Backtesting", 
                                    children=[
                                        rc.dash_bt.layout(),
                                    ],
                                    active_tab_style={
                                        "fontStyle": "italic",
                                    },
                                    active_label_style={
                                        "color": "#000000",
                                    }
                                ),
                                dbc.Tab(
                                    tab_id="pt-tab",
                                    label="Paper Trading",
                                    children=[

                                    ],
                                    active_tab_style={
                                        "fontStyle": "italic",
                                    },
                                    active_label_style={
                                        "color": "#000000",
                                    }
                                )
                            ]
                        )
                    ],
                )
            ],
            className="gx-0",
            style={
                "display": "flex"
            }
        ),
        dcc.Store(id="stock-data-store")
    ],
    fluid=True
)

async def fetch_stock(search_stock):
    cached_df = db_conn.is_cached(search_stock)
    if cached_df is not None:
        return cached_df.to_dict(as_series=False)

    vtr = vTrade()
    resp = await vtr.get_stocks_async([search_stock])
    df = resp[search_stock]
    if df is not None and not df.is_empty():
        db_conn.create_table(df, search_stock)
        return df.to_dict(as_series=False)
    else:
        logger.debug(f"No data for {search_stock} is fetched")
        return {}

@callback (
    Output("stock-data-store", "data"),
    Input("search-button", "n_clicks"),
    State("search-stock", "value"),
)
def update_stock_data(_, search_stock):
    try:
        result = asyncio.run(fetch_stock(search_stock))
        return result
    except Exception as _:
        return dash.no_update

rc.register_RMS_plot_callbacks()
rc.register_backtest_plot_callback()

if __name__ == "__main__":
    app.run_server(debug=True)