import polars as pl 
import plotly.graph_objects as go
from loguru import logger
from utils import *
import aiohttp

from strategy import Strategy

class StrategyRSI(Strategy):
    delta = "delta"
    gain = "gain"
    loss = "loss"
    avg_gain = "avg_gain"
    avg_loss = "avg_loss"
    RS = "rs"
    RSI = "rsi"

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
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    result = self.__process_response(data)
                    logger.debug(f"Received crossing MA response for {stock}")
                    print(result)
                    return result
                else:
                    logger.error(f"Failed to fetch cross MA signal for {stock}")
                    return None

    def show(self, df: pl.DataFrame, upper_bound=80, lower_bound=20) -> go.Figure | None:
        if not utils.check_list_substr_in_str(["rsi", "datetime"], df.columns):
            logger.debug("Dataframe columns do not contain RSI")
            
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