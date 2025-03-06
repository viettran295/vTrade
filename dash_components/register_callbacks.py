from dash import callback, Input, Output, State, exceptions
from utils import *
from strategy import StrategyCrossingMA, vTrade
from .dash_crossing_ma import DashCrossingMA
from .dash_backtesting import DashBackTesting
from .dash_checklist import DashChecklist
from .dash_tabs import DashTabs
from .db import ConnectDB
from backtesting import BackTesting

class RegisterCallbacks():
    def __init__(self):
        self.dash_bt = DashBackTesting()
        self.x_ma = DashCrossingMA()
        self.checklist = DashChecklist()
        self.db = ConnectDB()
        self.tabs = DashTabs()
        self.not_display = {}, {"display": "none"}
        self.vtrade = vTrade()
        self.strategy_x_ma = StrategyCrossingMA()

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
            ma_type: str = "SMA",
        ):
            if stock_data_store is None or len(stock_data_store) == 0:
                return self.not_display
            
            df = self.db.get_stock_data(search_stock)
            if df is None:
                return self.not_display
                
            # Early return without calculating crossing MA
            if not checklist or self.checklist.x_ma_val not in checklist:
                return self.vtrade.show_stock_price(df), {"display": "block"}

            try:
                df = self.strategy_x_ma.execute(df, short_ma, long_ma, ma_type)
                self.db.update_columns(
                    df,
                    search_stock, 
                    {
                        self.strategy_x_ma.short_ma_type: "FLOAT", 
                        self.strategy_x_ma.long_ma_type: "FLOAT", 
                        self.strategy_x_ma.signal: "FLOAT"
                    },
                    df.columns[0]
                )
                if df is not None:
                    return self.strategy_x_ma.show(df, short_ma, long_ma, ma_type), {"display": "block"}
            except Exception as e:
                logger.error(f"Error plotting crossing MA: {e}")
                return self.not_display
    
            
    def register_backtest_plot_callback(self):
        @callback (
            Output(self.dash_bt.backtest_graph, "figure"),
            Input(self.tabs.id_layout, "active_tab"),
            State("search-stock", "value"),
            prevent_initial_call = True
        )
        def plot_backtest(tab_id, search_stock):
            if tab_id == self.tabs.backtesting_id:
                df = self.db.get_stock_data(search_stock)
                bt = BackTesting()
                bt.set_data(df)
                bt.run()
                return bt.show_report()
            else:
                raise exceptions.PreventUpdate 