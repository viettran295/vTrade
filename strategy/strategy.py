import polars as pl
import plotly.graph_objects as go
from abc import ABC, abstractmethod
import os

from utils.comm_interface import CommunicationInterface


class Strategy(ABC):
    def __init__(self, data_fetcher: CommunicationInterface) -> None:
        self.url = os.getenv("STRATEGY_PROCESSOR_URL", "http://strategy-processor:8000")
        self.columns = ["datetime", "high", "low", "open", "close"]
        self.signal = "signal"
        self.bin_signal = {"buy": 1, "sell": 0}
        self._data_fetcher = data_fetcher

    @abstractmethod
    def show(self, df: pl.DataFrame) -> go.Figure | None:
        return

    def show_stock_price(self, df: pl.DataFrame) -> go.Figure:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)

        fig.add_trace(
            go.Candlestick(
                x=df["datetime"].to_list(),
                open=df["open"].to_list(),
                close=df["close"].to_list(),
                high=df["high"].to_list(),
                low=df["low"].to_list(),
                name="Close price",
            )
        )
        fig.update_layout(
            title={"text": "Stock Price", "x": 0.5},
            font=dict(size=18),
        )
        return fig

    def show_no_data(
        self,
        stock: str | None = None,
        message: str = "NO DATA AVAILABLE",
        submessage: str | None = None,
    ) -> go.Figure:
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode="markers",
                hoverinfo="none",
                showlegend=False,
            )
        )

        stock_str = f" FOR '{stock.upper()}'" if stock and stock.strip() else ""
        header_text = f"■ {message}{stock_str}"

        if not submessage:
            if stock and stock.strip():
                submessage = (
                    f"No market data returned for security: <b>{stock.upper()}</b>.<br>"
                    "Please verify the ticker symbol or select a different asset."
                )
            else:
                submessage = (
                    "No security selected.<br>"
                    "Please enter a stock symbol in the sidebar search (e.g., AAPL, NVDA, TSLA)."
                )

        fig.add_annotation(
            text=(
                f"<span style='color: #ff3333; font-size: 16px; font-weight: bold;'>⚠ NO DATA AVAILABLE</span><br><br>"
                f"<span style='color: #ff6600; font-size: 13px; font-weight: bold;'>{header_text}</span><br><br>"
                f"<span style='color: #888888; font-size: 11px; line-height: 1.6;'>{submessage}</span>"
            ),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            align="center",
            bordercolor="#ff6600",
            borderwidth=1.5,
            borderpad=20,
            bgcolor="#0a0a0a",
            font=dict(
                family="Courier Prime, Courier New, monospace",
            ),
        )

        title_text = f"■ {getattr(self, 'title', 'INTERACTIVE CHART').upper()} — NO DATA"

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#000000",
            plot_bgcolor="#050505",
            font=dict(family="Courier Prime, Courier New, monospace", color="#e8e8e8"),
            title={
                "text": title_text,
                "x": 0.02,
                "xanchor": "left",
                "font": {"size": 13, "color": "#ff6600", "family": "Courier Prime, monospace"},
            },
            xaxis=dict(
                visible=True,
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                gridcolor="#1a0a00",
            ),
            yaxis=dict(
                visible=True,
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                gridcolor="#1a0a00",
            ),
            margin=dict(l=45, r=15, t=55, b=25),
            height=450,
        )
        return fig

