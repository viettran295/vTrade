import polars as pl 
import plotly.graph_objects as go
from loguru import logger
from utils import *
from strategy import Strategy

class StrategyCrossingMA(Strategy):
    def __init__(self, short_MA: int=20, long_MA: int=50):
        super().__init__()
        self.short_ma_type = ""
        self.long_ma_type = ""
        self.short_ma = short_MA
        self.long_ma = long_MA

    @log_exectime
    def calc_MA(self, df: pl.DataFrame, length: int=20, ma_type: str="SMA") -> pl.DataFrame:
        if df is None:
            logger.error("DataFrame is None")
            return 
        if not isinstance(length, int) or not isinstance(ma_type, str):
            logger.error("Inputs are invalid")
            return

        try:
            col_name = ma_type + str(length)
            if "SMA" == ma_type:
                # Simple moving average
                df = df.with_columns(
                    pl.col("high").rolling_mean(window_size=length).alias(col_name),
                )
                logger.info("SMA is calculated")
            elif "EWM" == ma_type:
                # Exponentially weighted moving average
                df = df.with_columns(
                        pl.col("high").ewm_mean(span=length).alias(col_name),
                    )
                logger.info("EWM is calculated")
            else:
                logger.warning("Moving average type is not supported")
                return
        except Exception as e:
            logger.error(f"Error while calculating MA: {e}")
            return
        
        return df

    @log_exectime
    def execute(self, df: pl.DataFrame, short_MA: int=20, long_MA: int=50, ma_type: str="SMA") -> pl.DataFrame:
        if not utils.df_is_none(df):
            if isinstance(short_MA, int) or isinstance(long_MA, int):
                self.short_ma = short_MA
                self.long_ma = long_MA
            else:
                logger.error("Length of MA is invalid")
                return df
            try:
                df = self.calc_MA(df, self.short_ma, ma_type)
                df = self.calc_MA(df, self.long_ma, ma_type)

                self.short_ma_type = ma_type + str(self.short_ma)
                self.long_ma_type = ma_type + str(self.long_ma)
                self.signal = self.__generate_signal_cfg_name(self.short_ma, self.long_ma, ma_type)

                df = df.with_columns([
                    # Short MA crossing over long MA -> buying point
                    pl.when((pl.col(self.short_ma_type) > pl.col(self.long_ma_type)) & (pl.col(self.short_ma_type).shift(1) <= pl.col(self.long_ma_type).shift(1)))
                    .then(self.bin_signal["buy"])
                    # Short MA crossing down long MA -> selling point
                    .when((pl.col(self.short_ma_type) < pl.col(self.long_ma_type)) & (pl.col(self.short_ma_type).shift(1) >= pl.col(self.long_ma_type).shift(1)))
                    .then(self.bin_signal["sell"])
                    .otherwise(None)
                    .alias(self.signal)
                ])
                logger.info("Sell-buy signal for crossing MA is generated")
                return df
            except Exception as e:
                logger.error(f"Error while implementing Cross MA: {e}")
                return
        else:
            logger.error("DataFrame is None")
            return df
    
    def show(self, df: pl.DataFrame, short_MA: int, long_MA: int, ma_type: str="SMA") -> go.Figure:
        if not utils.df_is_none(df):
            if self.short_ma_type == "" or self.long_ma_type == "":
                logger.debug("Dataframe columns do not contain MA types")
                df = self.execute(df, short_MA, long_MA, ma_type)
        else:
            logger.error(f"Dataframe for MA calculation is None")
            return

        self.signal = self.__generate_signal_cfg_name(short_MA, long_MA, ma_type)
        signal_buy = df.filter(df[self.signal] == 1)
        signal_sell = df.filter(df[self.signal] == 0)
        
        self.fig.data = []
        self.fig = self.show_stock_price(df)

        self.fig.add_trace(go.Scatter(
                                x=df["datetime"].to_list(),
                                y=df[f"{self.short_ma_type}"].to_list(),
                                name=f"{self.short_ma_type}",
                                marker=dict(
                                    color="antiquewhite"
                                )
                            )
            )
        
        self.fig.add_trace(go.Scatter(
                                x=df["datetime"].to_list(),
                                y=df[f"{self.long_ma_type}"].to_list(),
                                name=f"{self.long_ma_type}",
                                marker=dict(
                                    color="lightblue"
                                )
                            )
            )
            
        self.fig.add_trace(go.Scatter(
                                x=signal_buy["datetime"].to_list(),
                                y=signal_buy[self.short_ma_type].to_list(), mode="markers",
                                marker=dict(size=9, 
                                            symbol="triangle-up",
                                            color="green"), 
                                name="Buying signal"
                            )
            )

        self.fig.add_trace(go.Scatter(
                                x=signal_sell["datetime"].to_list(),
                                y=signal_sell[self.short_ma_type].to_list(), mode="markers",
                                marker=dict(size=9, symbol="triangle-down",
                                            color="red"), 
                                name="Selling signal"
                            )
            )
        
        self.fig.update_layout(
                    title={
                        "text": "Crossing MA",
                        "x": 0.5
                    },
                    font=dict(size=18)
                )
        return self.fig
    
    def __generate_signal_cfg_name(self, short_MA: int, long_MA: int, ma_type: str="SMA"):
        return f"Signal_{ma_type}_{short_MA}_{long_MA}"