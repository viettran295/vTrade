import plotly.graph_objects as go
from utils import *
from strategy import Strategy
from strategy.crossing_ma import StrategyCrossingMA

class StrategyBollingerBands(Strategy):
    def __init__(self, moving_avg: int=20, standard_deviation: int=2):
        self.moving_avg = moving_avg
        self.nr_std = standard_deviation
        self.strategy_x_ma = StrategyCrossingMA() 
        self.title = "Bollinger Bands"
        self.upper_band = "Upper_band"
        self.lower_band = "Lower_band"

    @log_exectime
    def execute(self, df: pl.DataFrame) -> pl.DataFrame:
        if utils.df_is_none(df):
            return None

        try:
            self.signal = f"Signal_BB_MA{self.moving_avg}_STD{self.nr_std}"

            df = self.strategy_x_ma.calc_MA(df, self.moving_avg)
            df = df.with_columns(
                (pl.col(self.strategy_x_ma.short_ma_type) + self.nr_std * pl.col("close").rolling_std(window_size=self.moving_avg)).alias(self.upper_band),
                (pl.col(self.strategy_x_ma.short_ma_type) - self.nr_std * pl.col("close").rolling_std(window_size=self.moving_avg)).alias(self.lower_band)
            )

            df = df.with_columns([
                pl.when(pl.col("high") > pl.col(self.upper_band)).then(0)
                  .when(pl.col("low") < pl.col(self.lower_band)).then(1)
                  .otherwise(None)
                  .alias(self.signal)
            ])
            return df
        except Exception as e:
            logger.error(f"Error while calculating Bollinger bands: {e}")
    
    def show(self, df: pl.DataFrame) -> go.Figure:
        if (
            utils.df_is_none(df) or 
            not utils.check_list_substr_in_str([self.lower_band, self.upper_band, self.moving_avg], df.columns)
        ):
            logger.error("Invalid DataFrame")
            return None
        
        overbound = df.filter((pl.col("high") > pl.col(self.upper_band)))
        underbound = df.filter((pl.col("low") < pl.col(self.lower_band)))

        self.fig.data = []
        # Remove horizontal lines if exist
        self.fig.layout.pop('shapes')

        self.fig.add_trace(go.Candlestick(
                                x=df["datetime"].to_list(),
                                open=df["open"].to_list(), 
                                close=df["close"].to_list(), 
                                high=df["high"].to_list(),
                                low=df["low"].to_list(),
                                name=self.title,
                            )
                        )
        self.fig.add_trace(go.Scatter(
                        x=df["datetime"].to_list(),
                        y=df[self.strategy_x_ma.short_ma_type].to_list(),
                        name=self.strategy_x_ma.short_ma_type,
                    )
                )
        self.fig.add_trace(go.Scatter(
                        x=df["datetime"].to_list(),
                        y=df[self.lower_band].to_list(),
                        name=self.lower_band,
                    )
                )
        self.fig.add_trace(go.Scatter(
                        x=df["datetime"].to_list(),
                        y=df[self.upper_band].to_list(),
                        name=self.upper_band,
                        fill='tonexty',
                        opacity=0.1
                    )
                )
        self.fig.add_trace(go.Scatter(
                        x=overbound["datetime"].to_list(),
                        y=overbound["high"].to_list(),
                        name="Over bought",
                        mode="markers",
                    )           
                )
        self.fig.add_trace(go.Scatter(
                        x=underbound["datetime"].to_list(),
                        y=underbound["low"].to_list(),
                        name="Over sell",
                        mode="markers",
                    )           
                )
        self.fig.update_layout(
                        title={
                            "text": self.title,
                            "xanchor": "center",
                            "x": 0.5
                        },
                        font=dict(size=18)
                )
        return self.fig
