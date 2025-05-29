import polars as pl 
import plotly.graph_objects as go
from loguru import logger

from utils import *
from strategy import Strategy

class StrategyRSI(Strategy):
    RSI = ""

    def __init__(self, period: int=14, upper_bound: int=80, lower_bound: int=20):
        super().__init__()
        self.period = period
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
            
    async def fetch_rsi_signal(
            self, 
            stock: str
        ) -> pl.DataFrame | None:
        url = self.url + "/rsi/" + stock 
        response = await self._fetch_data(url)
        if response:
            data = self.__process_response(response)
            return data

    async def fetch_best_performance(
            self, 
            stock: str
        ) -> pl.DataFrame | None:
        url = self.url + "/bestperf/rsi/" + stock 
        response = await self._fetch_data(url)
        if response:
            data = self.__process_response(response)
            return data
        
    def show(self, df: pl.DataFrame, upper_bound=80, lower_bound=20) -> go.Figure | None:
        if not utils.check_list_substr_in_str(["rsi", "datetime"], df.columns):
            logger.debug("Dataframe columns do not contain RSI")
            return 
        
        if not self.__columns_exist(df):
            logger.error("Columns in DataFrame for MA calculation are missing")
            return
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)

        fig.add_trace(go.Scatter(
                                y=df[self.RSI].to_list(), 
                                x=df["datetime"].to_list(), 
                                name=self.RSI,
                                marker=dict(
                                    color="antiquewhite"
                                )
                            )
                        )
        fig.add_hline(y=upper_bound, line_dash="dash", line_color="red")
        fig.add_hline(y=lower_bound, line_dash="dash", line_color="red")
        # Add the filled region
        fig.add_shape(type="rect",
                      x0=min(df["datetime"].to_list()),
                      x1=max(df["datetime"].to_list()),
                      y0=lower_bound,
                      y1=upper_bound,
                      fillcolor="rgba(255, 0, 0, 0.1)",  # Red with 20% opacity
                      line_width=0)

        overbougt = df.filter(pl.col(self.RSI) > upper_bound)
        oversold = df.filter(pl.col(self.RSI) < lower_bound)
        fig.add_trace(go.Scatter(y=overbougt[self.RSI].to_list(), x=overbougt["datetime"].to_list(), 
                                      mode="markers", marker=dict(color='red'), name="Over bought"))
        fig.add_trace(go.Scatter(y=oversold[self.RSI].to_list(), x=oversold["datetime"].to_list(), 
                                      mode="markers", marker=dict(color="green"), name="Over sold"))

        fig.update_layout(
                    title={
                        "text": "Relative strength index (RSI) plot",
                        "x": 0.5
                    },
                    font=dict(size=18)
                )
        return fig

    def __columns_exist(self, df: pl.DataFrame) -> bool:
        for col in df.columns:
            match col:
                case col_name if "RSI" in col_name:
                    self.RSI = col_name
                case col_name if "Sig" in col_name:
                    self.signal = col_name
        if self.RSI == "" or self.signal == "":
            return False
        return True
    
    @staticmethod
    def __process_response(data: dict) -> pl.DataFrame | None:
        if "data" in data and "columns" in data:
            df = pl.DataFrame(data['data'])
            df = df.with_columns(
                pl.col(df.columns[0]).str.strptime(pl.Datetime).cast(pl.Date),
                *[pl.col(i).cast(pl.Float64) for i in df.columns[1:]], # Unpack list
            )
            new_names = data["columns"]["column_names"]
            rename_dict = dict(zip(df.columns, new_names))
            df = df.rename(rename_dict)
            df = df.sort(by=pl.col("datetime"), descending=False)
            return df
        else:
            return None