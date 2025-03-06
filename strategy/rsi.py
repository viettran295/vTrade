import polars as pl 
import plotly.graph_objects as go
from loguru import logger
from utils import *

from strategy import Strategy

class StrategyRSI(Strategy):
    delta = "delta"
    gain = "gain"
    loss = "loss"
    avg_gain = "avg_gain"
    avg_loss = "avg_loss"
    RS = "RS"
    RSI = "self"

    def __init__(self, period: int=14, upper_bound: int=80, lower_bound: int=20):
        super().__init__()
        self.period = period
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
     
    @log_exectime
    def calc_RSI(
        self, 
        df: pl.DataFrame, 
        period: int = 14
    ) -> pl.DataFrame:    

        if utils.df_is_none(df):
            return None
                
        try:
            # Calculate difference between previous day
            df =  df.with_columns(
                (pl.col("close") - pl.col("close").shift(1)).alias(self.delta)
            )
            # Calculate gain and loss
            df = df.with_columns(
                pl.when(pl.col(self.delta) > 0).then(pl.col(self.delta)).otherwise(0).alias(self.gain),
                pl.when(pl.col(self.delta) < 0).then(-pl.col(self.delta)).otherwise(0).alias(self.loss)
            )
            # Calculate average gains and losses over a rolling window
            df = df.with_columns(
                pl.col(self.gain).rolling_mean(window_size=period, min_periods=1).alias(self.avg_gain),
                pl.col(self.loss).rolling_mean(window_size=period, min_periods=1).alias(self.avg_loss)
            )
            # Calculate RS and self
            df = df.with_columns(
                (pl.col(self.avg_gain) / pl.col(self.avg_loss)).alias(self.RS),
            )
            df = df.with_columns(
                (100 - (100 / (1 + pl.col(self.RS)))).alias(self.RSI)
            )
            logger.info(f"Calculated RSI: P{period}")
            return df
        
        except Exception as e:
            logger.error("Error while calculating self: ", e)
            return None
    
    def execute(
            self, 
            df: pl.DataFrame,
            upper_bound: int=80,
            lower_bound: int=20,
            period:int = 14
    ) -> pl.DataFrame:
        
        if utils.df_is_none(df) or not self.__check_and_set_cfg(period, upper_bound, lower_bound):
            return None
        
        try:
            if self.RSI not in df.columns:
                df = self.calc_RSI(df, period)
            self.signal = self.__generate_signal_cfg_name(period, upper_bound, lower_bound)

            # Calculate signal
            df = df.with_columns(
                pl.when(pl.col(self.RSI) > self.upper_bound).then(self.bin_signal["sell"])
                .when(pl.col(self.RSI) < self.lower_bound).then(self.bin_signal["buy"])
                .otherwise(None)
                .alias(self.signal)
            )
            logger.info("Sell-buy signal for rsi is generated")
            return df
        except Exception as e:
            logger.error(f"Error while calculating signal: {e}")
            return df


    def show(self, df: pl.DataFrame, upper_bound=80, lower_bound=20) -> go.Figure:
        if not utils.check_list_substr_in_str(["RSI", "datetime"], df.columns):
            logger.debug("Dataframe columns do not contain RSI")
            df = self.execute(df)
        self.fig.data = []

        self.fig.add_trace(go.Scatter(y=df[self.RSI].to_list(), x=df["datetime"].to_list(), name=self.RSI))
        self.fig.add_hline(y=upper_bound, line_dash="dash", line_color="red")
        self.fig.add_hline(y=lower_bound, line_dash="dash", line_color="red")

        overbougt = df.filter(pl.col(self.RSI) > upper_bound)
        oversold = df.filter(pl.col(self.RSI) < lower_bound)
        self.fig.add_trace(go.Scatter(y=overbougt[self.RSI].to_list(), x=overbougt["datetime"].to_list(), 
                                      mode="markers", marker=dict(color='red'), name="Over bought"))
        self.fig.add_trace(go.Scatter(y=oversold[self.RSI].to_list(), x=oversold["datetime"].to_list(), 
                                      mode="markers", marker=dict(color="green"), name="Over sold"))

        self.fig.update_layout(
                    title={
                        "text": "Relative strength index (RSI) plot",
                        "x": 0.5
                    },
                    font=dict(size=18)
                )
        return self.fig

    def __generate_signal_cfg_name(self, period: int, upper_bound: int, lower_bound: int) -> str:
        return f"Signal_RSI_P{period}_U{upper_bound}_L{lower_bound}"
    
    def __check_and_set_cfg(self, period: int, upper_bound: int, lower_bound: int) -> bool:
        if not isinstance(upper_bound, int) or \
            not isinstance(lower_bound, int) or \
            not isinstance(period, int):
            logger.error("Inputs are invalid")
            return False
        else:
            self.period = period
            self.upper_bound = upper_bound
            self.lower_bound = lower_bound
            return True
