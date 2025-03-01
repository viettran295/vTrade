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
        self.not_display = {}, {"display": "none"}

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
            if stock_data_store is None or len(stock_data_store) == 0:
                return self.not_display
            
            df = self.db.get_stock_data(search_stock)
            if df is None:
                return self.not_display
            
            strategy = Strategy()

            # Early return without calculating crossing MA
            if not checklist or self.checklist.x_ma_val not in checklist:
                return strategy.show_stock_price(df), {"display": "block"}

            short_ma = ma_types + str(short_ma)
            long_ma= ma_types + str(long_ma)
            x_ma = f"{strategy.sell_buy_sig}_{short_ma}_{long_ma}"
            # Calculate missing indicators
            if short_ma not in df.columns:
                df = strategy.calc_MA(df, short_ma)
            if long_ma not in df.columns:
                df = strategy.calc_MA(df, long_ma)
            if x_ma not in df.columns:
                df = strategy.calc_crossing_MA(df, short_ma, long_ma)
                self.db.update_columns(
                    df,
                    search_stock, 
                    {
                        short_ma: "FLOAT", 
                        long_ma: "FLOAT", 
                        x_ma: "FLOAT"
                    },
                    strategy.columns[0]
                )
            if df is not None:
                return strategy.show_crossing_MA(df, short_ma, long_ma), {"display": "block"}
            
            return self.not_display
    
            
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