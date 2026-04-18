from dash import callback, Input, Output, State
import asyncio

from utils.comm_interface import *
from strategy import StrategyCrossingMA, StrategyRSI, StrategyBollingerBands
from fundamental import FinancialStatement, BalanceSheet
from common import FUNDAMENTAL_DATA_CACHE_ID

from .dash_crossing_ma import DashCrossingMA
from .dash_rsi import DashRSI
from .dash_bb import DashBollingerBands
from .dash_checklist import DashChecklist
from .dash_tabs import DashTabs
from .dash_balance_sheet import DashBalanceSheet
from .dash_cash_flow import DashCashFlow


class RegisterCallbacks:
    def __init__(self):
        self.x_ma = DashCrossingMA()
        self.dash_rsi = DashRSI()
        self.dash_bb = DashBollingerBands()
        self.checklist = DashChecklist()
        self.tabs = DashTabs()
        self.dash_balance_sheet = DashBalanceSheet()
        self.dash_cash_flow = DashCashFlow()

        self.not_display = {}, {"display": "none"}
        self.display = {"display": "block"}

        self.strategy_x_ma = StrategyCrossingMA(HttpComm)
        self.strategy_rsi = StrategyRSI(HttpComm)
        self.strategy_bb = StrategyBollingerBands(HttpComm)
        self.strategy_name = ""

        self.financial_statement = FinancialStatement()
        self.financial_statement._data_fetcher = HttpComm
        self.balance_sheet = BalanceSheet()

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
                            search_stock, short_ma, long_ma, ma_type
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
            prevent_initial_call=True,
        )
        def plot_best_performance_ma(
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
                    logger.error(f"Error plotting best performance crossing MA: {e}")
                    return self.not_display
            return self.not_display

    def register_best_performance_RSI(self):
        @callback(
            Output(self.dash_rsi.rsi_graph_id, "figure", allow_duplicate=True),
            Output(self.dash_rsi.id_layout, "style", allow_duplicate=True),
            Input(self.dash_rsi.bestperf_button, "n_clicks"),
            State("search-stock", "value"),
            prevent_initial_call=True,
        )
        def plot_best_performance_rsi(
            _,
            search_stock,
        ):
            if search_stock:
                try:
                    df = asyncio.run(
                        self.strategy_rsi.fetch_best_performance(search_stock)
                    )
                    if df is not None:
                        return self.strategy_rsi.show(df), self.display
                except Exception as e:
                    logger.error(f"Error plotting best performance RSI: {e}")
                    return self.not_display
            return self.not_display

    def register_RSI_plot_callback(self):
        @callback(
            Output(self.dash_rsi.rsi_graph_id, "figure"),
            Output(self.dash_rsi.id_layout, "style"),
            Input(self.checklist.id, "value"),
            State("search-stock", "value"),
        )
        def plot_rsi(checklist, search_stock):
            if self.checklist.rsi_val in checklist:
                try:
                    df_rsi = asyncio.run(
                        self.strategy_rsi.fetch_rsi_signal(search_stock)
                    )
                    if df_rsi is not None:
                        return self.strategy_rsi.show(df_rsi), self.display
                except Exception as e:
                    logger.error(f"Error plotting RSI: {e}")
                    return self.not_display
            else:
                return self.not_display

    def register_BB_plot_callback(self):
        @callback(
            Output(self.dash_bb.bb_graph_id, "figure"),
            Output(self.dash_bb.id_layout, "style"),
            Input(self.checklist.id, "value"),
            State("search-stock", "value"),
        )
        def plot_bb(checklist, search_stock):
            if self.checklist.bb_val in checklist:
                try:
                    df_bb = asyncio.run(self.strategy_bb.fetch_bb_signal(search_stock))
                    if df_bb is not None:
                        return self.strategy_bb.show(df_bb), self.display
                except Exception as e:
                    logger.error(f"Error plotting Bollinger Bands: {e}")
                    return self.not_display
            else:
                return self.not_display

    def register_best_performance_BB(self):
        @callback(
            Output(self.dash_bb.bb_graph_id, "figure", allow_duplicate=True),
            Output(self.dash_bb.id_layout, "style", allow_duplicate=True),
            Input(self.dash_bb.bestperf_button, "n_clicks"),
            State("search-stock", "value"),
            prevent_initial_call=True,
        )
        def plot_best_performance_bb(
            _,
            search_stock,
        ):
            if search_stock:
                try:
                    df = asyncio.run(
                        self.strategy_bb.fetch_best_performance(search_stock)
                    )
                    if df is not None:
                        return self.strategy_bb.show(df), self.display
                except Exception as e:
                    logger.error(f"Error plotting best performance BB: {e}")
                    return self.not_display
            return self.not_display

    def register_fundamental_balance_sheet(self):
        @callback(
            Output(self.dash_balance_sheet.id_balance_sheet_graph, "figure"),
            Output(self.dash_balance_sheet.id_layout, "style"),
            Input(FUNDAMENTAL_DATA_CACHE_ID, "data"),
            prevent_initial_call=True,
        )
        def plot_fundamental_balance_sheet(data):
            try:
                if data is not None:
                    validated_fs = self.financial_statement.model_validate(data)
                    if validated_fs.balance_sheet:
                        return (
                            validated_fs.show_balance_sheet(),
                            self.display,
                        )
            except Exception as e:
                logger.error(f"Error showing balance sheet: {e}")
                return self.not_display
            return self.not_display

    def register_fundamental_cash_flow(self):
        @callback(
            Output(self.dash_cash_flow.id_cash_flow_graph, "figure"),
            Output(self.dash_cash_flow.id_layout, "style"),
            Input(FUNDAMENTAL_DATA_CACHE_ID, "data"),
            prevent_initial_call=True,
        )
        def plot_fundamental_cash_flow(data):
            try:
                if data is not None:
                    validated_fs = self.financial_statement.model_validate(data)
                    if validated_fs.cash_flow:
                        return (
                            validated_fs.show_cash_flow(),
                            self.display,
                        )
            except Exception as e:
                logger.error(f"Error showing cash flow: {e}")
                return self.not_display
            return self.not_display
