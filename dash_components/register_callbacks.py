from dash import callback, Input, Output, State
from utils import *
from strategy import StrategyCrossingMA, StrategyRSI
import dash

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
            Output(self.dash_rsi.id_layout, "style"),
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

            Input(self.x_ma.backtest_button, "n_clicks"),
            State(self.x_ma.backtest_button, "children"),
            Input(self.checklist.id, "value"),

            State("search-stock", "value"),
            State(self.x_ma.short_ma_input, "value"),
            State(self.x_ma.long_ma_input, "value"),
            State(self.x_ma.ma_types, "value"),
            prevent_initial_call=True,
        )
        def plot_backtest_crossing_ma(
            _,
            button_state,
            checklist: str,
            search_stock: str,
            short_ma: int = 20,
            long_ma: int = 50,
            ma_type: str = "SMA",
        ):
            x_ma_output = self.not_display
            ctx = dash.callback_context

            if button_state == self.x_ma.state_hide_bt:
                return x_ma_output

            df = self.db.get_stock_data(search_stock)
            if df_is_none(df):
                return x_ma_output
            
            if self.checklist.x_ma_val in checklist and \
                ctx.triggered_id == self.x_ma.backtest_button:

                try:
                    bt = BackTesting()
                    bt.set_data(df)
                    self.strategy_name = f"Signal_{ma_type}_{short_ma}_{long_ma}"
                    if self.strategy_name in df.columns:
                        bt.run(self.strategy_name)
                        x_ma_output = bt.show_report(self.strategy_name), self.display
                except Exception as e:
                    logger.error(f"Error backtesting {self.strategy_name}: {e}")
                    x_ma_output = self.not_display

            return x_ma_output
        
        @callback(
            Output(self.dash_bt.rsi_graph_id, "figure"),
            Output(self.dash_bt.rsi_graph_id, "style"),

            Input(self.dash_rsi.backtest_button, "n_clicks"),
            State(self.dash_rsi.backtest_button, "children"),
            Input(self.checklist.id, "value"),

            State("search-stock", "value"),
            prevent_initial_call=True,
        )
        def plot_backtest_crossing_ma(
            _,
            button_state,
            checklist: str,
            search_stock: str,
        ):
            x_ma_output = self.not_display
            ctx = dash.callback_context

            if button_state == self.x_ma.state_hide_bt:
                return x_ma_output

            df = self.db.get_stock_data(search_stock)
            if df_is_none(df):
                return x_ma_output

            if self.checklist.rsi_val in checklist and \
                ctx.triggered_id == self.dash_rsi.backtest_button:
                try:
                    bt = BackTesting()
                    bt.set_data(df)
                    self.strategy_name = "Signal_RSI_P14_U80_L20"
                    if self.strategy_name in df.columns:
                        bt.run(self.strategy_name)
                        x_ma_output = bt.show_report(self.strategy_name), self.display
                except Exception as e:
                    logger.error(f"Error backtesting {self.strategy_name}: {e}")
                    x_ma_output = self.not_display

            return x_ma_output
    
    
    def register_backtest_buttons_callback(self):
        @callback (
            Output(self.x_ma.backtest_button, "children"),
            Input(self.x_ma.backtest_button, "n_clicks"),
            State(self.x_ma.backtest_button, "children"),
            prevent_initial_call=True,
        )
        def change_crossing_ma_btn_state(_, state):
            return change_btn_state(state)

        @callback (
            Output(self.dash_rsi.backtest_button, "children"),
            Input(self.dash_rsi.backtest_button, "n_clicks"),
            State(self.dash_rsi.backtest_button, "children"),
            prevent_initial_call=True,
        )
        def change_rsi_btn_state(_, state):
            return change_btn_state(state)
        
        def change_btn_state(state):
            show = "Show backtesting"
            hide = "Hide backtesting"
            if state == show:
                return hide
            else:
                return show