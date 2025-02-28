from dash import callback, Input, Output, State
from utils import *
from strategy import Strategy
import duckdb
from .dash_crossing_ma import DashCrossingMA
from .dash_backtesting import DashBackTesting
from .dash_checklist import DashChecklist
from .db import ConnectDB
from backtesting import BackTesting

class RegisterCallbacks():
    def __init__(self):
        self.dash_bt = DashBackTesting()
        self.x_ma = DashCrossingMA()
        self.checklist = DashChecklist()
        self.db = ConnectDB()

    def register_RMS_plot_callbacks(self):
        @callback(
            Output(self.x_ma.crossing_ma_graph, "figure"),
            Output(self.x_ma.id_layout, "style"),
            Input(self.x_ma.apply_crossing_ma_button, "n_clicks"),
            Input("stock-data-store", "data"),
            Input(self.checklist.id, "value"),
            State("search-stock", "value"),
            State(self.x_ma.short_ma_input, "value"),
            State(self.x_ma.long_ma_input, "value"),
            State(self.x_ma.ma_types, "value"),
        )
        def plot_crossing_ma(
            _,
            stock_data_store, 
            checklist,
            search_stock,
            short_ma: int = 20,
            long_ma: int = 50,
            ma_types: str = "SMA",
        ):
            not_display = {}, {"display": "none"}
            if stock_data_store is None or len(stock_data_store) == 0:
                return not_display
            
            df = self.db.get_stock_data(search_stock)
            if df is None:
                return not_display
            
            strategy = Strategy()

            if not checklist or self.checklist.x_ma_val not in checklist:
                return strategy.show_stock_price(df), {"display": "block"}

            short_ma = ma_types + '_' + str(short_ma)
            long_ma= ma_types + '_' + str(long_ma)
            df = strategy.calc_MA(df, short_ma)
            df = strategy.calc_MA(df, long_ma)
            df = strategy.calc_crossing_MA(df, short_ma, long_ma)
            if df is not None:
                self.db.update_stock_data(df, search_stock)
                return strategy.show_crossing_MA(df, short_ma, long_ma), {"display": "block"}
            else:
                return not_display
    
            
    def register_backtest_plot_callback(self):
        # @callback (
        #     Output(self.dash_bt.backtest_graph, "figure"),
        #     Output(self.dash_bt.id_layout, "style"),
        #     State("search-stock", "value"),
        #     prevent_initial_call = True
        # )
        # def plot_backtest(_, button_content, search_stock):
        #     show = "Show backtest"
        #     hide = "Hide backtest"
        #     if show == button_content:
        #         db_conn = duckdb.connect(DB_PATH)
        #         df = db_conn.execute(f"SELECT * FROM {search_stock}").pl()
        #         bt = BackTesting()
        #         bt.set_data(df)
        #         bt.run()
        #         return bt.show_report(), {"display": "block"}, hide
        #     else:
        #         return {}, {"display": "none"}, show
        pass