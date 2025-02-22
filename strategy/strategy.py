import polars as pl
from loguru import logger
import plotly.graph_objects as go
from utils import *

class Strategy:
    
    fig = go.Figure()
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)

    def __init__(self) -> None:
        self.columns = ["open", "close", "high", "close"]
        self.sell_buy_sig = "Signal"
        self.signal = {
            "buy": 1,
            "sell": 0
        }

    @log_exectime
    def calc_MA(self, df: pl.DataFrame, MA_length: str) -> pl.DataFrame:
        if df is None:
            logger.error("DataFrame is None")
            return 
        
        length = int(MA_length.split("_")[-1])

        try:
            if "SMA" in MA_length:
                df = df.with_columns(
                    pl.col("high").rolling_mean(window_size=length).alias(MA_length),
                )
                logger.info("SMA is calculated")
            elif "EWM" in MA_length:
                # Exponentially weighted moving average
                df = df.with_columns(
                        pl.col("high").ewm_mean(span=length).alias(MA_length),
                    )
                logger.info("EWM is calculated")
        except Exception as e:
            logger.error(f"Error while calculating MA  --> {e}")
            return
        return df
    
    @utils.log_exectime
    def calc_crossing_MA(self, df: pl.DataFrame, short_MA: str, long_MA: str) -> pl.DataFrame:
        if not utils.df_is_none(df):
            if short_MA in df and long_MA in df:
                try:
                    df = df.with_columns([
                        # Short MA crossing over long MA -> buying point
                        pl.when((pl.col(short_MA) > pl.col(long_MA)) & (pl.col(short_MA).shift(1) <= pl.col(long_MA).shift(1)))
                        .then(self.signal["buy"])
                        # Short MA crossing down long MA -> selling point
                        .when((pl.col(short_MA) < pl.col(long_MA)) & (pl.col(short_MA).shift(1) >= pl.col(long_MA).shift(1)))
                        .then(self.signal["sell"])
                        .otherwise(None)
                        .alias(self.sell_buy_sig)
                    ])
                    logger.info("Calculated crossing MA points")
                    logger.info("Sell-buy signal for crossing MA is generated")
                    return df
                except Exception as e:
                    logger.error("Error while implementing Cross MA")
                    return
            else:
                logger.error(f"{short_MA} or {long_MA} not in Dataframe")
        else:
            logger.error("DataFrame is None")
    
    def show_crossing_MA(self, df: pl.DataFrame, short_MA: str, long_MA: str) -> go.Figure():
        if not utils.df_is_none(df):
            if short_MA not in df and long_MA not in df:
                logger.debug("Dataframe columns do not contain MA types")
                df = self.calc_crossing_MA(df, short_MA, long_MA)
        else:
            logger.error(f"Dataframe for MA calculation is None")
            return

        signal_buy = df.filter(df[self.sell_buy_sig] == 1)
        signal_sell = df.filter(df[self.sell_buy_sig] == 0)
        
        self.fig.data = []
        self.fig.add_trace(go.Bar(
                                x=df["datetime"].to_list(), 
                                y=df["high"].to_list(), 
                                name="Price",
                                marker=dict(color='white')
                            )
            )

        for ma_type in [short_MA, long_MA]:
            self.fig.add_trace(go.Scatter(
                                    x=df["datetime"].to_list(),
                                    y=df[f"{ma_type}"].to_list(),
                                    name=f"{ma_type}"
                                )
                )
            
        self.fig.add_trace(go.Scatter(
                                x=signal_buy["datetime"].to_list(),
                                y=signal_buy[short_MA].to_list(), mode="markers",
                                marker=dict(size=9, 
                                            symbol="triangle-up",
                                            color="green"), 
                                name="Buying signal"
                            )
            )

        self.fig.add_trace(go.Scatter(
                                x=signal_sell["datetime"].to_list(),
                                y=signal_sell[short_MA].to_list(), mode="markers",
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
        return self.fig
    
    @utils.log_exectime
    def calc_RSI(
            self, 
            df: pl.DataFrame, 
            upper_bound: int = 80, 
            lower_bound: int = 20, 
            period: int = 14
        ) -> pl.DataFrame:    

        if utils.df_is_none(df):
            return None
        
        try:
            rsi = RSI()
            # Calculate difference between previous day
            df_rsi =  df.with_columns(
                (pl.col("close") - pl.col("close").shift(1)).alias(rsi.delta)
            )
            # Calculate gain and loss
            df_rsi = df_rsi.with_columns(
                pl.when(pl.col(rsi.delta) > 0).then(pl.col(rsi.delta)).otherwise(0).alias(rsi.gain),
                pl.when(pl.col(rsi.delta) < 0).then(-pl.col(rsi.delta)).otherwise(0).alias(rsi.loss)
            )
            # Calculate average gains and losses over a rolling window
            df_rsi = df_rsi.with_columns(
                pl.col(rsi.gain).rolling_mean(window_size=period, min_periods=1).alias(rsi.avg_gain),
                pl.col(rsi.loss).rolling_mean(window_size=period, min_periods=1).alias(rsi.avg_loss)
            )
            # Calculate RS and RSI
            df_rsi = df_rsi.with_columns(
                (pl.col(rsi.avg_gain) / pl.col(rsi.avg_loss)).alias(rsi.RS),
            )
            df_rsi = df_rsi.with_columns(
                (100 - (100 / (1 + pl.col(rsi.RS)))).alias(rsi.RSI)
            )
            logger.info("Calculated RSI")

            # Calculate signal
            df_rsi = df_rsi.with_columns(
                pl.when(pl.col(rsi.RSI) > upper_bound).then(self.signal["sell"])
                .when(pl.col(rsi.RSI) < lower_bound).then(self.signal["buy"])
                .otherwise(None)
                .alias(self.sell_buy_sig)
            )
            logger.info("Sell-buy signal for RSI is generated")
            return df_rsi
        except Exception as e:
            print(e)
            logger.error("Error while calculating RSI: ", e)
            return None
        
    def show_RSI(self, df_rsi: pl.DataFrame, upper_bound=80, lower_bound=20) -> go.Figure():
        if not utils.check_list_substr_in_str(["RSI", "datetime"], df_rsi.columns):
            logger.debug("Dataframe columns do not contain RSI")
            df_rsi = self.calc_RSI(df_rsi)
        self.fig.data = []
        self.fig.add_trace(go.Line(y=df_rsi["RSI"].to_list(), x=df_rsi["datetime"].to_list(), name="RSI"))
        
        self.fig.add_hline(y=upper_bound, line_dash="dash", line_color="red")
        self.fig.add_hline(y=lower_bound, line_dash="dash", line_color="red")

        overbougt = df_rsi.filter(pl.col("RSI") > upper_bound)
        oversold = df_rsi.filter(pl.col("RSI") < lower_bound)
        self.fig.add_trace(go.Scatter(y=overbougt["RSI"].to_list(), x=overbougt["datetime"].to_list(), 
                                      mode="markers", marker=dict(color='red'), name="Over bought"))
        self.fig.add_trace(go.Scatter(y=oversold["RSI"].to_list(), x=oversold["datetime"].to_list(), 
                                      mode="markers", marker=dict(color="green"), name="Over sold"))

        self.fig.update_layout(
                    title={"text": "Relative strength index (RSI) plot",
                            "xanchor": "center",
                            "x": 0.5},
                )
        return self.fig

    @utils.log_exectime
    def calc_bollinger_bands(self, df: pl.DataFrame) -> pl.DataFrame:
        if utils.df_is_none(df):
            return None

        bb = BollingerBands()

        try:
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
    
    def show_bollinger_bands(self, df: pl.DataFrame) -> go.Figure():
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
                        title={"text": bb.title,
                                "xanchor": "center",
                                "x": 0.5},
                        )
        return self.fig

class RSI():
    def __init__(self) -> None:
        self.delta = "delta"
        self.gain = "gain"
        self.loss = "loss"
        self.avg_gain = "avg_gain"
        self.avg_loss = "avg_loss"
        self.RS = "RS"
        self.RSI = "RSI"
    
class BollingerBands():
    def __init__(self):
        self.title = "Bollinger Bands"
        self.upper_band = "Upper_band"
        self.lower_band = "Lower_band"
        self.moving_avg = "SMA_20"
        self.nr_std = 2
        self.std_window = int(self.moving_avg.split("_")[-1])