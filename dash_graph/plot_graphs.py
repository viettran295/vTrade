from dash import callback, Input, Output, State
from utils import *
from strategy import Strategy
import duckdb

def register_RMS_plot_callbacks():
    @callback(
        Output("crossing_ma_graph", "figure"),
        Output("crossing_ma_graph", "style"),
        Input("stock_data_store", "data"),
        State("search_stock", "value"),
    )
    def plot_crossing_ma(stock_data_store, search_stock):
        if stock_data_store is None or len(stock_data_store) == 0:
            return {}, {"display": "none"}
        strategy = Strategy()
        db_conn = duckdb.connect(DB_PATH)
        df = db_conn.execute(f"SELECT * FROM {search_stock}").pl()
        short_ma: str = "EWM_20"
        long_ma: str = "EWM_50"
        df = strategy.calc_MA(df, short_ma)
        df = strategy.calc_MA(df, long_ma)
        df = strategy.calc_crossing_MA(df, short_ma, long_ma)
        if df is not None:
            return strategy.show_crossing_MA(df, short_ma, long_ma), {"display": "block"}
        else:
            return {}, {"display": "none"}