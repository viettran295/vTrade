from dash import callback, Input, Output, State, exceptions
from utils import *
from strategy import StrategyCrossingMA, StrategyRSI

from .dash_crossing_ma import DashCrossingMA
from .dash_rsi import DashRSI
from .dash_backtesting import DashBackTesting
from .dash_checklist import DashChecklist
from .dash_tabs import DashTabs

from .db import ConnectDB
from backtesting import BackTesting

class RegisterCallbacks():
    def __init__(self):
        self.dash_bt = DashBackTesting()
        self.x_ma = DashCrossingMA()
        self.dash_rsi = DashRSI()
        self.checklist = DashChecklist()
        self.tabs = DashTabs()

        self.db = ConnectDB()
        self.not_display = {}, {"display": "none"}
        self.display = {"display": "block"}

        self.vtrade = vTrade()
        self.strategy_x_ma = StrategyCrossingMA()
        self.strategy_rsi = StrategyRSI()
        self.strategy_name = ""

    def register_MA_plot_callbacks(self):
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
            self.strategy_name = f"Signal_{ma_type}_{short_ma}_{long_ma}"
            if not checklist or self.checklist.x_ma_val not in checklist:
                return self.strategy_x_ma.show_stock_price(df), self.display
            elif self.strategy_name in df:
                return self.strategy_x_ma.show(df, short_ma, long_ma, ma_type), self.display
            
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
                    return self.strategy_x_ma.show(df, short_ma, long_ma, ma_type), self.display
            except Exception as e:
                logger.error(f"Error plotting crossing MA: {e}")
                return self.not_display
    
    def register_RSI_plot_callback(self):
        @callback (
            Output(self.dash_rsi.rsi_graph_id, "figure"),
            Output(self.dash_rsi.rsi_graph_id, "style"),
            Input(self.checklist.id, "value"),
            State("search-stock", "value"),
        )
        def plot_rsi(checklist, search_stock):
            if self.checklist.rsi_val in checklist:
                df = self.db.get_stock_data(search_stock)

                self.strategy_name = "Signal_RSI_P14_U80_L20"
                if df is not None and self.strategy_name in df.columns:
                    return self.strategy_rsi.show(df), self.display

                try:
                    df_rsi = self.strategy_rsi.execute(df)
                    self.db.update_columns(
                        df_rsi,
                        search_stock, 
                        {
                            self.strategy_rsi.RSI: "FLOAT",
                            self.strategy_rsi.signal: "FLOAT"
                        },
                        df_rsi.columns[0]
                    )
                    return self.strategy_rsi.show(df_rsi), self.display
                except Exception as e:
                    logger.error(f"Error plotting RSI: {e}")
                    return self.not_display
            else:
                return self.not_display
            
    def register_backtest_plot_callback(self):
        @callback(
            Output(self.dash_bt.x_ma_graph_id, "figure"),
            Output(self.dash_bt.x_ma_graph_id, "style"),
            Output(self.dash_bt.rsi_graph_id, "figure"),
            Output(self.dash_bt.rsi_graph_id, "style"),

            Input(self.tabs.id_layout, "active_tab"),
            Input(self.checklist.id, "value"),

            State("search-stock", "value"),
            State(self.x_ma.short_ma_input, "value"),
            State(self.x_ma.long_ma_input, "value"),
            State(self.x_ma.ma_types, "value"),
            prevent_initial_call=True,
        )
        def plot_backtest(
            tab_id: str,
            checklist: str,
            search_stock: str,
            short_ma: int = 20,
            long_ma: int = 50,
            ma_type: str = "SMA",
        ):
            x_ma_output = self.not_display
            rsi_output = self.not_display

            if tab_id == self.tabs.backtesting_id:
                df = self.db.get_stock_data(search_stock)
                if df_is_none(df):
                    return *x_ma_output, *rsi_output

                bt = BackTesting()
                bt.set_data(df)

                if self.checklist.x_ma_val in checklist:
                    try:
                        self.strategy_name = f"Signal_{ma_type}_{short_ma}_{long_ma}"
                        bt.run(self.strategy_name)
                        x_ma_output = bt.show_report(self.strategy_name), self.display
                    except Exception as e:
                        logger.error(f"Error backtesting {self.strategy_name}: {e}")
                        x_ma_output = self.not_display

                if self.checklist.rsi_val in checklist:
                    try:
                        self.strategy_name = "Signal_RSI_P14_U80_L20"
                        bt.run(self.strategy_name)
                        rsi_output = bt.show_report(self.strategy_name), self.display
                    except Exception as e:
                        logger.error(f"Error backtesting {self.strategy_name}: {e}")
                        rsi_output = self.not_display

            return *x_ma_output, *rsi_output