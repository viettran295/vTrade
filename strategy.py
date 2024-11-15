from vtrade import vTrade
import polars as pl
from loguru import logger
import plotly.graph_objects as go

class Strategy(vTrade):
    def __init__(self) -> None:
        super().__init__()
        self.sell_buy_sig = "Signal"

    def calc_crossing_MA(self, df: pl.DataFrame, short_MA: str, long_MA: str) -> pl.DataFrame:
        try:
            df = df.with_columns([
                # Short MA crossing over long MA -> buying point
                pl.when((pl.col(short_MA) > pl.col(long_MA)) & (pl.col(short_MA).shift(1) <= pl.col(long_MA).shift(1)))
                .then(1)
                # Short MA crossing down long MA -> selling point
                .when((pl.col(short_MA) < pl.col(long_MA)) & (pl.col(short_MA).shift(1) >= pl.col(long_MA).shift(1)))
                .then(0)
                .otherwise(None)
                .alias(self.sell_buy_sig)
            ])
            logger.info("Calculated crossing MA points")
            return df
        except Exception as e:
            logger.error("Error while implementing Cross MA")
            return
    
    def show_crossing_MA(self, df: pl.DataFrame, short_MA: str, long_MA: str):
        if not self._check_listSubstr_in_Str([short_MA, long_MA], df.columns):
            logger.debug("Dataframe columns do not contain MA types")
            df = self.calc_crossing_MA(df, short_MA, long_MA)

        signal_1 = df.filter(df[self.sell_buy_sig] == 1)
        signal_0 = df.filter(df[self.sell_buy_sig] == 0)
        
        self.fig.add_trace(go.Bar(x=df["datetime"], y=df["high"]))

        for ma_type in [short_MA, long_MA]:
            self.fig.add_trace(go.Line(x=df["datetime"],
                                    y=df[f"{ma_type}"],
                                    name=f"{ma_type}"))
            
        self.fig.add_trace(go.Scatter(x=signal_1["datetime"],
                                y=signal_1[short_MA], mode="markers",
                                marker=dict(size=9, symbol="triangle-up",
                                            color="green")))

        self.fig.add_trace(go.Scatter(x=signal_0["datetime"],
                                y=signal_0[short_MA], mode="markers",
                                marker=dict(size=9, symbol="triangle-down",
                                            color="red")))

        self.fig.show()