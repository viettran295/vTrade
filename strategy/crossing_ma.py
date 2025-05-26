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
        url = self.url + ma_type + stock + f"?short_ma={short_ma}&long_ma={long_ma}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    result = self.__process_response(data)
                    logger.debug(f"Received crossing MA response for {stock}")
                    return result
                else:
                    logger.error(f"Failed to fetch cross MA signal for {stock}")
                    return None

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
        for col in df.columns:
            match col:
                case col_name if "short" in col_name:
                    self.short_ma_type = col_name
                case col_name if "long" in col_name:
                    self.long_ma_type = col_name
                case col_name if "Sig" in col_name:
                    self.signal = col_name
        if self.short_ma_type == "" or \
            self.long_ma_type == "" or \
            self.signal == "":
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