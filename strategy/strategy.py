import polars as pl
import plotly.graph_objects as go
from utils import *
from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self) -> None:
        self.url = "http://localhost:8000"
        self.columns = ["datetime", "open", "close", "high", "low"]
        self.signal = ""
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