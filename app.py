from dash import Dash, html, callback, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import duckdb
import utils
import os
from dash_components import RegisterCallbacks
from dotenv import load_dotenv
load_dotenv()
from loguru import logger
from strategy import vTrade

dbc_css = "https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/minty/bootstrap.min.css"

app = Dash(
    title="__vTrade__",
    external_stylesheets=[dbc.themes.DARKLY, dbc_css]
)

utils.clean_up_db()
rc = RegisterCallbacks()

DB_PATH = os.getenv("DUCKDB_PATH")

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
                                                html.H4("Technical indicators"),
                                                dcc.Checklist(
                                                    options=[
                                                        {
                                                            'label': html.Div(['Crossing MA'], 
                                                                            style={'color': utils.colors["text"], 'font-size': 20,}
                                                                    ),
                                                            'value': 'x_ma',
                                                             
                                                        },
                                                        {
                                                            'label': html.Div(['RSI'], 
                                                                            style={'color': utils.colors["text"], 'font-size': 20}
                                                                    ),
                                                            'value': 'rsi'
                                                        },
                                                        {
                                                            'label': html.Div(['Bollinger bands'], 
                                                                            style={'color': utils.colors["text"], 'font-size': 20}
                                                                    ),
                                                            'value': 'b_bands'
                                                        }
                                                    ],
                                                    value=['x_ma'],
                                                    labelStyle={"display": "flex", "align-items": "center",},
                                                )
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
                            style={
                                "width": "300px",
                            },
                        )
                    ],
                    width=3
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

@callback (
    Output("stock-data-store", "data"),
    Input("search-button", "n_clicks"),
    State("search-stock", "value"),
)
def fetch_stock(_, search_stock):
    db_conn = duckdb.connect(DB_PATH)
    tables = db_conn.execute("SHOW TABLES").fetchall()
    tables_list = [row[0] for row in tables]
    if search_stock in tables_list:
        logger.debug(f"{search_stock} is already cached")
        df = db_conn.execute(f"SELECT * FROM {search_stock}").pl()
        return df.to_dict(as_series=False)

    vtr = vTrade()
    df = vtr.get_stock_data(search_stock)
    if df is not None and not df.is_empty():
        db_conn.execute(f"CREATE TABLE IF NOT EXISTS {search_stock} AS SELECT * FROM df")
        logger.info(f"Fetched and cached {search_stock}")
        return df.to_dict(as_series=False)
    else:
        logger.debug(f"No data for {search_stock} is fetched")
        return {}

rc.register_RMS_plot_callbacks()
rc.register_backtest_plot_callback()

if __name__ == "__main__":
    app.run_server(debug=True)