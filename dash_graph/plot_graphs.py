from dash import callback, Input, Output, State
from utils import *
from strategy import Strategy
import duckdb
from .components import CrossingMA

x_ma = CrossingMA()

def register_RMS_plot_callbacks():
    @callback(
        Output(x_ma.crossing_ma_graph, "figure"),
        Output(x_ma.id_layout, "style"),
        Input(x_ma.apply_crossing_ma_button, "n_clicks"),
        Input("stock_data_store", "data"),
        State("search_stock", "value"),
        State(x_ma.short_ma_input, "value"),
        State(x_ma.long_ma_input, "value"),
        State(x_ma.ma_types, "value"),
    )
    def plot_crossing_ma(
        _,
        stock_data_store, 
        search_stock,
        short_ma: int = 20,
        long_ma: int = 50,
        ma_types: str = "SMA",
    ):
        if stock_data_store is None or len(stock_data_store) == 0:
            return {}, {"display": "none"}
        strategy = Strategy()
        db_conn = duckdb.connect(DB_PATH)
        df = db_conn.execute(f"SELECT * FROM {search_stock}").pl()
        short_ma = ma_types + '_' + str(short_ma)
        long_ma= ma_types + '_' + str(long_ma)
        df = strategy.calc_MA(df, short_ma)
        df = strategy.calc_MA(df, long_ma)
        df = strategy.calc_crossing_MA(df, short_ma, long_ma)
        if df is not None:
            return strategy.show_crossing_MA(df, short_ma, long_ma), {"display": "block"}
        else:
            return {}, {"display": "none"}