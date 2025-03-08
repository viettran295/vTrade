from optimizer import Optimizer
from strategy import StrategyCrossingMA
from backtesting import BackTesting
import numpy as np
import polars as pl
from utils import *
from loguru import logger

class OptimizerCrossingMA(Optimizer):
    def __init__(
            self, 
            strategy: StrategyCrossingMA, 
            backtesting: BackTesting,
            short_ma_range: np.arange=np.arange(10, 100, 5), 
            long_short_diff: np.arange=np.arange(5, 100, 5)
    ):
        super().__init__()
        self.strategy = strategy
        self.backtesting = backtesting
        self.short_ma_range = short_ma_range
        self.long_short_diff = long_short_diff 
        self.ma_type = ["SMA", "EWM"]

        self.max_profit = -np.inf
        self.optimized_short_ma = None
        self.optimized_long_ma = None
        self.df_result = None

    def setup(self, short_ma_range: np.arange, long_short_diff: np.arange):
        self.short_ma_range= short_ma_range
        self.long_short_diff = long_short_diff

    @log_exectime
    def optimize(self, df: pl.DataFrame):
        if df_is_none(df):
            logger.error("Dataframe is invalid")

        self.df_result = df
        for short_ma in self.short_ma_range:
            for diff in self.long_short_diff:
                long_ma = short_ma + diff
                self.df_result = self.strategy.execute(self.df_result, short_ma, long_ma)

                strategy_name = f"Signal_{self.ma_type[0]}_{short_ma}_{long_ma}"
                self.backtesting.set_data(self.df_result)
                self.backtesting.run(strategy_name)

                # Get max profit in every backtesting
                curr_max_profit = max(self.backtesting.results[self.backtesting.profit_col])
                if curr_max_profit > self.max_profit:
                    self.max_profit = curr_max_profit
                    self.optimized_short_ma = short_ma
                    self.optimized_long_ma = long_ma
                    logger.debug(f"Current max profit: {self.max_profit} \n\
                                    Optimized short MA: {short_ma} - long MA: {long_ma}")
    
    def show_result(self):
        if  self.df_result is None or \
            self.optimized_short_ma is None or \
            self.optimized_long_ma is None:

            logger.error("Invalid parameters")
            return
        else:
            return self.strategy.show(self.df_result, int(self.optimized_short_ma), int(self.optimized_long_ma))
        