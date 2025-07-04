import polars as pl
import plotly.graph_objects as go
import aiohttp
from abc import ABC, abstractmethod

from utils import *

class Strategy(ABC):
    def __init__(self) -> None:
        self.url = "http://localhost:8000"
        self.columns = ["datetime", "high", "low", "open", "close"]
        self.signal = "signal"
        self.bin_signal = {
            "buy": 1,
            "sell": 0
        }
    
    @abstractmethod
    def show(self, df: pl.DataFrame) -> go.Figure | None:
        return
    
    def show_stock_price(self, df: pl.DataFrame) -> go.Figure:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)

        fig.add_trace(go.Candlestick(
                        x=df["datetime"].to_list(),
                        open=df["open"].to_list(), 
                        close=df["close"].to_list(), 
                        high=df["high"].to_list(),
                        low=df["low"].to_list(),
                        name="Close price",
                    )
        )
        fig.update_layout(
            title={
                "text": "Stock Price",
                "x": 0.5
            },
            font=dict(size=18),
        )
        return fig

    async def _fetch_data(self, endpoint: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"Received response from {endpoint}")
                    return data
                else:
                    logger.error(f"Failed to fetch data from {endpoint}")
                    return None