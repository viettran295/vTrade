import aiohttp
import polars as pl 
import plotly.graph_objects as go
from loguru import logger
import utils
from strategy import Strategy

class StrategyCrossingMA(Strategy):
    def __init__(self, short_MA: int=20, long_MA: int=50):
        super().__init__()
        self.short_ma_type = ""
        self.long_ma_type = ""
        self.short_ma = short_MA
        self.long_ma = long_MA

    async def fetch_cross_ma_signal(
            self, 
            stock: str, 
            short_ma: int=20, 
            long_ma: int=50,
            ma_type: str="sma",
        ):
        ma_type = '/' + ma_type.lower() + '/'
        endpoint = self.url + ma_type + stock + f"?short_ma={short_ma}&long_ma={long_ma}"
        response = await self._fetch_data(endpoint)
        if response is not None:
            data = self.__process_response(response)
            return data

    async def fetch_best_performance(
            self, 
            stock: str, 
            ma_type: str="sma",
        ):
        prefix = '/bestperf/' + ma_type.lower() + '/'
        url = self.url + prefix + stock
        response = await self._fetch_data(url)
        if response is not None:
            data = self.__process_response(response)
            return data

    def show(self, df: pl.DataFrame) -> go.Figure | None:
        if utils.df_is_none(df):
            logger.error("Dataframe for MA calculation is None")
            return

        if not self.__columns_exist(df):
            logger.error("Columns in DataFrame for MA calculation are missing")
            return

        signal_buy = df.filter(df[self.signal] == -1)
        signal_sell = df.filter(df[self.signal] == 1)

        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)

        fig = self.show_stock_price(df)

        fig.add_trace(go.Scatter(
                                x=df["datetime"].to_list(),
                                y=df[f"{self.short_ma_type}"].to_list(),
                                name=f"{self.short_ma_type}",
                                line=dict(
                                    color="#FFFF00",
                                    width=2
                                )
                            )
            )

        fig.add_trace(go.Scatter(
                                x=df["datetime"].to_list(),
                                y=df[f"{self.long_ma_type}"].to_list(),
                                name=f"{self.long_ma_type}",
                                fill='tonexty',
                                line=dict(
                                    color="white",
                                    width=2
                                )
                            )
            )

        fig.add_trace(go.Scatter(
                                x=signal_buy["datetime"].to_list(),
                                y=signal_buy[self.short_ma_type].to_list(), mode="markers",
                                marker=dict(
                                    size=12, 
                                    symbol="triangle-up",
                                    color="lawngreen"
                                ), 
                                name="Buying signal"
                            )
            )

        fig.add_trace(go.Scatter(
                                x=signal_sell["datetime"].to_list(),
                                y=signal_sell[self.short_ma_type].to_list(), mode="markers",
                                marker=dict(
                                    size=12, 
                                    symbol="triangle-down",
                                    color="red"
                                ), 
                                name="Selling signal"
                            )
            )

        fig.update_layout(
                    title={
                        "text": "Crossing MA",
                        "x": 0.5
                    },
                    font=dict(size=18)
                )
        return fig

    def __columns_exist(self, df: pl.DataFrame) -> bool:
        ma_cols = []
        for col in df.columns:
            if "Sig" in col:
                self.signal = col
            elif "SMA" in col or "EWMA" in col:
                ma_cols.append(col)
        ma_cols = sorted(ma_cols)
        self.short_ma_type = ma_cols[0]
        self.long_ma_type = ma_cols[1]
        if self.short_ma_type == "" or \
            self.long_ma_type == "" or \
            self.signal == "":
            return False
        return True

    def __process_response(self, data: dict) -> pl.DataFrame | None:
        if "data" in data and "columns" in data:
            df = pl.DataFrame(data['data'])
            ma_window_1 = "ma_window_1"
            ma_window_2 = "ma_window_2"
            ma_windows = "ma_windows"

            df = df.with_columns([
                pl.col(ma_windows).map_elements(lambda x: x[0] if len(x) > 0 else None).alias(ma_window_1),
                pl.col(ma_windows).map_elements(lambda x: x[1] if len(x) > 1 else None).alias(ma_window_2),
            ])

            df = df.drop(ma_windows)

            df = df.with_columns(
                pl.col(df.columns[0]).str.strptime(pl.Datetime).cast(pl.Date),
                *[pl.col(i).cast(pl.Float64) for i in df.columns[1:]], # Unpack list
            )

            new_pos_cols = self.columns + [ma_window_1, ma_window_2, "signal"]
            df = df.select(new_pos_cols)

            new_names = data["columns"]["column_names"]
            rename_dict = dict(zip(df.columns, new_names))
            df = df.rename(rename_dict)
            df = df.sort(by=pl.col("datetime"), descending=False)
            return df
        else:
            return None
        