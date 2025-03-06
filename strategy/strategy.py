import polars as pl
from loguru import logger
import plotly.graph_objects as go
from utils import *
import re
from abc import ABC, abstractmethod

class Strategy(ABC):
    
    fig = go.Figure()
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)

    def __init__(self) -> None:
        self.columns = ["datetime", "open", "close", "high", "low"]
        self.signal = ""
        self.bin_signal = {
            "buy": 1,
            "sell": 0
        }
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def show(self):
        return
    
    def show_stock_price(self, df: pl.DataFrame) -> go.Figure:
        self.fig.data = []
        self.fig.add_trace(go.Bar(
                        x=df["datetime"].to_list(), 
                        y=df["close"].to_list(), 
                        name="Close price",
                        marker=dict(color='white')
                    )
        )
        self.fig.update_layout(
            title={
                "text": "Stock Price",
                "x": 0.5
            },
            font=dict(size=18),
        )
        return self.fig
    

    @utils.log_exectime
    def calc_bollinger_bands(self, df: pl.DataFrame) -> pl.DataFrame:
        if utils.df_is_none(df):
            return None

        bb = BollingerBands()

        try:
            self.sell_buy_sig = f"Signal_BB_MVA{bb.moving_avg}_STD{bb.nr_std}"
            df = self.calc_MA(df, bb.moving_avg)
            df = df.with_columns(
                (pl.col(bb.moving_avg) + bb.nr_std * pl.col("close").rolling_std(window_size=bb.std_window)).alias(bb.upper_band),
                (pl.col(bb.moving_avg) - bb.nr_std * pl.col("close").rolling_std(window_size=bb.std_window)).alias(bb.lower_band)
            )

            df = df.with_columns([
                pl.when(pl.col("high") > pl.col(bb.upper_band)).then(self.signal["sell"])
                  .when(pl.col("low") < pl.col(bb.lower_band)).then(self.signal["buy"])
                  .otherwise(None)
                  .alias(self.sell_buy_sig)
            ])
            return df
        except Exception as e:
            logger.error(f"Error while calculating Bollinger bands: {e}")
    
    def show_bollinger_bands(self, df: pl.DataFrame) -> go.Figure:
        bb = BollingerBands()

        if (
            utils.df_is_none(df) or 
            not utils.check_list_substr_in_str(self.columns, df.columns) or 
            not utils.check_list_substr_in_str([bb.lower_band, bb.upper_band, bb.moving_avg], df.columns)
        ):
            logger.error("Invalid DataFrame")
            return None
        
        overbound = df.filter((pl.col("high") > pl.col(bb.upper_band)))
        underbound = df.filter((pl.col("low") < pl.col(bb.lower_band)))

        self.fig.data = []
        # Remove horizontal lines if exist
        self.fig.layout.pop('shapes')

        self.fig.add_trace(go.Candlestick(
                                x=df["datetime"].to_list(),
                                open=df["open"].to_list(), 
                                close=df["close"].to_list(), 
                                high=df["high"].to_list(),
                                low=df["low"].to_list(),
                                name=bb.title,
                            )
                        )
        self.fig.add_trace(go.Line(
                        x=df["datetime"].to_list(),
                        y=df[bb.moving_avg].to_list(),
                        name=bb.moving_avg,
                    )
                )
        self.fig.add_trace(go.Line(
                        x=df["datetime"].to_list(),
                        y=df[bb.lower_band].to_list(),
                        name=bb.lower_band,
                    )
                )
        self.fig.add_trace(go.Line(
                        x=df["datetime"].to_list(),
                        y=df[bb.upper_band].to_list(),
                        name=bb.upper_band,
                        fill='tonexty'
                    )
                )
        self.fig.add_trace(go.Scatter(
                        x=overbound["datetime"].to_list(),
                        y=overbound["high"].to_list(),
                        mode="markers",
                    )           
                )
        self.fig.add_trace(go.Scatter(
                        x=underbound["datetime"].to_list(),
                        y=underbound["low"].to_list(),
                        mode="markers",
                    )           
                )
        self.fig.update_layout(
                        title={
                            "text": bb.title,
                            "xanchor": "center",
                            "x": 0.5
                        },
                        font=dict(size=18)
                )
        return self.fig

class BollingerBands():
    def __init__(self):
        self.title = "Bollinger Bands"
        self.upper_band = "Upper_band"
        self.lower_band = "Lower_band"
        self.moving_avg = "SMA20"
        self.nr_std = 2
        match = re.match(r"([a-zA-Z]+)(\d+)", self.moving_avg)
        self.std_window = int(match.group(2))