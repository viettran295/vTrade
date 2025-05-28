from dash import callback, Input, Output, State
from utils import *
from strategy import StrategyCrossingMA, StrategyRSI
import dash
import asyncio

from .dash_crossing_ma import DashCrossingMA
from .dash_rsi import DashRSI
from .dash_checklist import DashChecklist
from .dash_tabs import DashTabs


class RegisterCallbacks():
    def __init__(self):
        self.x_ma = DashCrossingMA()
        self.dash_rsi = DashRSI()
        self.checklist = DashChecklist()
        self.tabs = DashTabs()

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
            Input("activate-search", "data"),
            Input(self.checklist.id, "value"),
            State("search-stock", "value"),
            State(self.x_ma.short_ma_input, "value"),
            State(self.x_ma.long_ma_input, "value"),
            State(self.x_ma.ma_types, "value"),
        )
        def plot_crossing_ma(
            _,
            __, 
            checklist,
            search_stock,
            short_ma: int = 20,
            long_ma: int = 50,
            ma_type: str = "SMA",
        ):
            if self.checklist.x_ma_val not in checklist:
                return self.not_display

            if search_stock:
                try:
                    df = asyncio.run(
                            self.strategy_x_ma.fetch_cross_ma_signal(
                                search_stock, 
                                short_ma, 
                                long_ma,
                                ma_type
                            )
                        )
                    if df is not None:
                        return self.strategy_x_ma.show(df), self.display
                except Exception as e:
                    logger.error(f"Error plotting crossing MA: {e}")
                    return self.not_display
            return self.not_display
        
    def register_best_performance_MA(self):
        @callback(
            Output(self.x_ma.crossing_ma_graph, "figure", allow_duplicate=True),
            Output(self.x_ma.id_layout, "style", allow_duplicate=True),
            Input(self.x_ma.bestperf_button, "n_clicks"),
            State("search-stock", "value"),
            State(self.x_ma.ma_types, "value"),
            prevent_initial_call=True
        )
        def plot_best_performance(
            _,
            search_stock,
            ma_type: str = "SMA",
        ):
            if search_stock:
                try:
                    df = asyncio.run(
                            self.strategy_x_ma.fetch_best_performance(search_stock, ma_type)
                        )
                    if df is not None:
                        return self.strategy_x_ma.show(df), self.display
                except Exception as e:
                    logger.error(f"Error plotting crossing MA: {e}")
                    return self.not_display
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
                try:
                    df_rsi = asyncio.run(self.strategy_rsi.fetch_rsi_signal(search_stock))
                    if df_rsi is not None:
                        return self.strategy_rsi.show(df_rsi), self.display
                except Exception as e:
                    logger.error(f"Error plotting RSI: {e}")
                    return self.not_display
            else:
                return self.not_display