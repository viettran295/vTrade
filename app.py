from dash import Dash, html, callback, Input, Output, State, dcc
import dash
import dash_bootstrap_components as dbc
import utils
from utils import vTrade
from dash_components import RegisterCallbacks, ConnectDB
from dotenv import load_dotenv
load_dotenv()
from loguru import logger
import asyncio

dbc_css = "https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/minty/bootstrap.min.css"

app = Dash(
    title="Trust the Algorithms",
    external_stylesheets=[dbc.themes.DARKLY, dbc_css, dbc.icons.FONT_AWESOME]
)
app._favicon = "bull_icon.ico"

rc = RegisterCallbacks()
db_conn = ConnectDB()
db_conn.clean_up_db()

app.layout = dbc.Container(
    style = {
        "backgroundColor": utils.colors["background"],
         "height": "100vh",
         "overflow": "hidden"
    },
    children = [
        dbc.Row(
            [                
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                html.Img(src="assets/bull_icon.png"),
                            ],
                            style={
                                "display": "flex",
                                "justify-content": "right",
                            }
                        )
                    ],
                    width=5
                ),
                dbc.Col(
                    [
                        html.H1(
                            "Trust the Algorithms",
                            style={
                                "textAlign": "left",
                                "color": utils.colors["text"],
                            }
                        ),
                    ],
                    width=5
                )
            ],
        ),
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
                    width=2,
                ),
                # Main Content
                dbc.Col(
                    [
                        rc.tabs.layout()
                    ],
                    style={
                        "maxHeight": "900px",  # Set a max height
                        "overflowY": "auto",  # Enable vertical scrolling when needed
                    },
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
        return df.write_json()
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

rc.register_MA_plot_callbacks()
rc.register_backtest_plot_callback()
rc.register_RSI_plot_callback()
rc.register_backtest_buttons_callback()

if __name__ == "__main__":
    app.run_server(debug=True)