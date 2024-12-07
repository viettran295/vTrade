from vtrade import vTrade
import polars as pl
from loguru import logger
import plotly.graph_objects as go

class Strategy(vTrade):
    def __init__(self) -> None:
        super().__init__()
        self.sell_buy_sig = "Signal"

    def calc_crossing_MA(self, df: pl.DataFrame, short_MA: str, long_MA: str) -> pl.DataFrame:
        if df is not None:
            if short_MA in df and long_MA in df:
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
            else:
                logger.error(f"{short_MA} or {long_MA} not in Dataframe")
        else:
            logger.error(f"{df} is None")
    
    def show_crossing_MA(self, df: pl.DataFrame, short_MA: str, long_MA: str):
        if df is not None:
            if short_MA not in df and long_MA not in df:
                logger.debug("Dataframe columns do not contain MA types")
                df = self.calc_crossing_MA(df, short_MA, long_MA)
        else:
            logger.error(f"Dataframe is None")
            return

        signal_buy = df.filter(df[self.sell_buy_sig] == 1)
        signal_sell = df.filter(df[self.sell_buy_sig] == 0)
        
        self.fig.data = []
        self.fig.add_trace(go.Bar(
                                x=df["datetime"], 
                                y=df["high"], 
                                name="Price",
                                marker=dict(color='white')
                            )
            )

        for ma_type in [short_MA, long_MA]:
            self.fig.add_trace(go.Line(
                                    x=df["datetime"],
                                    y=df[f"{ma_type}"],
                                    name=f"{ma_type}"
                                )
                )
            
        self.fig.add_trace(go.Scatter(
                                x=signal_buy["datetime"],
                                y=signal_buy[short_MA], mode="markers",
                                marker=dict(size=9, 
                                            symbol="triangle-up",
                                            color="green"), 
                                name="Buying signal"
                            )
            )

        self.fig.add_trace(go.Scatter(
                                x=signal_sell["datetime"],
                                y=signal_sell[short_MA], mode="markers",
                                marker=dict(size=9, symbol="triangle-down",
                                            color="red"), 
                                name="Selling signal"
                            )
            )
        
        self.fig.update_layout(
                    title={"text": "Crossing MA",
                            "xanchor": "center",
                            "x": 0.5},
                )
        self.fig.show()
    
    def calc_RSI(self, df: pl.DataFrame, period=14) -> pl.DataFrame:
        if "close" not in df.columns:
            logger.error("Dataframe does not contain 'close' column")
            return None
        try:
            # Calculate difference between previous day
            df_rsi =  df.with_columns(
                (pl.col("close") - pl.col("close").shift(1)).alias("delta")
            )
            # Calculate gain and loss
            df_rsi = df_rsi.with_columns(
                pl.when(pl.col("delta") > 0).then(pl.col("delta")).otherwise(0).alias("gain"),
                pl.when(pl.col("delta") < 0).then(-pl.col("delta")).otherwise(0).alias("loss")
            )
            # Calculate average gains and losses over a rolling window
            df_rsi = df_rsi.with_columns(
                pl.col("gain").rolling_mean(window_size=period, min_periods=1).alias("avg_gain"),
                pl.col("loss").rolling_mean(window_size=period, min_periods=1).alias("avg_loss")
            )
            # Calculate RS and RSI
            df_rsi = df_rsi.with_columns(
                (pl.col("avg_gain") / pl.col("avg_loss")).alias("RS"),
            )
            df_rsi = df_rsi.with_columns(
                (100 - (100 / (1 + pl.col("RS")))).alias("RSI")
            )
            logger.info("Calculated RSI")
            return df_rsi
        except Exception as e:
            print(e)
            logger.error("Error while calculating RSI: ", e)
            return None
        
    def show_RSI(self, df_rsi: pl.DataFrame, upper_bound=80, lower_bound=20):
        if not self._check_listSubstr_in_Str(["RSI", "datetime"], df_rsi.columns):
            logger.debug("Dataframe columns do not contain RSI")
            df_rsi = self.calc_RSI(df_rsi)
        self.fig.data = []
        self.fig.add_trace(go.Line(y=df_rsi["RSI"], x=df_rsi["datetime"], name="RSI"))
        
        self.fig.add_hline(y=upper_bound, line_dash="dash", line_color="red")
        self.fig.add_hline(y=lower_bound, line_dash="dash", line_color="red")

        overbougt = df_rsi.filter(pl.col("RSI") > upper_bound)
        oversold = df_rsi.filter(pl.col("RSI") < lower_bound)
        self.fig.add_trace(go.Scatter(y=overbougt["RSI"], x=overbougt["datetime"], 
                                      mode="markers", marker=dict(color='red'), name="Over bought"))
        self.fig.add_trace(go.Scatter(y=oversold["RSI"], x=oversold["datetime"], 
                                      mode="markers", marker=dict(color="green"), name="Over sold"))

        self.fig.update_layout(
                    title={"text": "Relative strength index (RSI) plot",
                            "xanchor": "center",
                            "x": 0.5},
                )
        self.fig.show()