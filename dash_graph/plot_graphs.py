from dash import callback, Input, Output, State
from utils import *
from strategy import Strategy
import duckdb
from .dash_crossing_ma import DashCrossingMA
from .dash_backtesting import DashBackTesting
from backtesting import BackTesting

dash_bt = DashBackTesting()
x_ma = DashCrossingMA(dash_bt)

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
            db_conn.execute(f"CREATE OR REPLACE TABLE {search_stock} AS SELECT * FROM df")
            logger.debug(f"Updated table {search_stock} with crossing MA columns")
            return strategy.show_crossing_MA(df, short_ma, long_ma), {"display": "block"}
        else:
            return {}, {"display": "none"}
        
def register_backtest_plot_callback():
    @callback (
        Output(dash_bt.backtest_graph, "figure"),
        Output(dash_bt.id_layout, "style"),
        Output(x_ma.show_backtest_button, "children"),
        Input(x_ma.show_backtest_button, "n_clicks"),
        State(x_ma.show_backtest_button, "children"),
        State("search_stock", "value"),
        prevent_initial_call = True
    )
    def plot_backtest(_, button_content, search_stock):
        show = "Show backtest"
        hide = "Hide backtest"
        if show == button_content:
            db_conn = duckdb.connect(DB_PATH)
            df = db_conn.execute(f"SELECT * FROM {search_stock}").pl()
            bt = BackTesting()
            bt.set_data(df)
            bt.run()
            return bt.show_report(), {"display": "block"}, hide
        else:
            return {}, {"display": "none"}, show