from vtrade import vTrade
import polars as pl
from loguru import logger
import plotly.graph_objects as go

class Strategy(vTrade):
    def __init__(self) -> None:
        super().__init__()
        self.sell_buy_sig = "Signal"

    def calc_crossing_MA(self, df: pl.DataFrame, MA1: str, MA2: str) -> pl.DataFrame:
        try:
            df = df.with_columns([
                pl.when((pl.col(MA1) > pl.col(MA2)) & (pl.col(MA1).shift(1) <= pl.col(MA2).shift(1)))
                .then(1)
                .when((pl.col(MA1) < pl.col(MA2)) & (pl.col(MA1).shift(1) >= pl.col(MA2).shift(1)))
                .then(0)
                .otherwise(None)
                .alias(self.sell_buy_sig)
            ])
            logger.info("Calculated crossing MA points")
            return df
        except Exception as e:
            logger.error("Error while implementing Cross MA")
            return
    
    def show_crossing_MA(self, df: pl.DataFrame, MA1: str, MA2: str):
        if not self._check_listSubstr_in_Str([MA1, MA2], df.columns):
            logger.debug("Dataframe columns do not contain MA types")
            df = self.calc_crossing_MA(df, MA1, MA2)

        signal_1 = df.filter(df[self.sell_buy_sig] == 1)
        signal_0 = df.filter(df[self.sell_buy_sig] == 0)
        
        self.fig.add_trace(go.Bar(x=df["datetime"], y=df["high"]))

        for ma_type in [MA1, MA2]:
            self.fig.add_trace(go.Line(x=df["datetime"],
                                    y=df[f"{ma_type}"],
                                    name=f"{ma_type}"))
            
        self.fig.add_trace(go.Scatter(x=signal_1["datetime"],
                                y=signal_1[MA1], mode="markers",
                                marker=dict(size=9, symbol="triangle-up",
                                            color="green")))

        self.fig.add_trace(go.Scatter(x=signal_0["datetime"],
                                y=signal_0[MA1], mode="markers",
                                marker=dict(size=9, symbol="triangle-down",
                                            color="red")))

        self.fig.show()