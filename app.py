from dash import Dash, html, callback, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import duckdb
import utils
import os
from dash_graph import plot_graphs, CrossingMA, DashBackTesting
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
dash_bt = DashBackTesting()
x_ma = CrossingMA(dash_bt)

DB_PATH = os.getenv("DUCKDB_PATH")

app.layout = html.Div(
    style = {
        "backgroundColor": utils.colors["background"],
         "height": "100vh",
    },
    children = [
        html.H1(
            "vTrade App",
            style={
                "textAlign": "center",
                "color": utils.colors["text"],
            }
        ),
        html.Br(),
        html.Div(
            children = [
                dbc.Input(
                    id="search_stock",
                    type="text",
                    placeholder="Enter your stock symbol",
                    style={
                        "justifyContent": "left",
                        "marginRight": "10px",
                        "width": "250px"
                    },
                ),
                dbc.Button(
                    id="search_button",
                    children="Search",
                    target="blank",
                    n_clicks=0,
                    color="success",
                    style={
                        "marginLeft": "10px"
                    },
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center" 
            },
        ),
        html.Br(),
        x_ma.layout(),
        html.Br(),
        dash_bt.layout(),
        dcc.Store(id="stock_data_store")
    ]
)

@callback (
    Output("stock_data_store", "data"),
    Input("search_button", "n_clicks"),
    State("search_stock", "value"),
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

plot_graphs.register_RMS_plot_callbacks()
plot_graphs.register_backtest_plot_callback()

if __name__ == "__main__":
    app.run_server(debug=True)