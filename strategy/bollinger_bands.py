import plotly.graph_objects as go
from utils import *
from strategy import Strategy
from strategy.crossing_ma import StrategyCrossingMA

class StrategyBollingerBands(Strategy):
    def __init__(self):
        super().__init__()
        self.title = "Bollinger Bands"
        self.moving_avg = ""
        self.upper_band = ""
        self.lower_band = ""
        self.sig = ""

    async def fetch_bb_signal(
            self, 
            stock: str
        ) -> pl.DataFrame | None:
        url = self.url + "/bb/" + stock 
        response = await self._fetch_data(url)
        if response:
            data = self.__process_response(response)
            return data
    
    def show(self, df: pl.DataFrame) -> go.Figure:
        if utils.df_is_none(df):
            logger.error("Invalid DataFrame")
            return None

        if not self.__columns_exist(df):
            logger.error("Invalid DataFrame")
            return None
        
        overbound = df.filter((pl.col("high") > pl.col(self.upper_band)))
        underbound = df.filter((pl.col("low") < pl.col(self.lower_band)))

        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        # Remove horizontal lines if exist
        # self.fig.layout.pop('shapes')

        fig.add_trace(go.Candlestick(
                                x=df["datetime"].to_list(),
                                open=df["open"].to_list(), 
                                close=df["close"].to_list(), 
                                high=df["high"].to_list(),
                                low=df["low"].to_list(),
                                name=self.title,
                            )
                        )
        fig.add_trace(go.Scatter(
                        x=df["datetime"].to_list(),
                        y=df[self.moving_avg].to_list(),
                        name=self.moving_avg,
                    )
                )
        fig.add_trace(go.Scatter(
                        x=df["datetime"].to_list(),
                        y=df[self.lower_band].to_list(),
                        name=self.lower_band,
                    )
                )
        fig.add_trace(go.Scatter(
                        x=df["datetime"].to_list(),
                        y=df[self.upper_band].to_list(),
                        name=self.upper_band,
                        fill='tonexty',
                        fillcolor='rgba(255, 255, 255, 0.2)',
                    )
                )
        fig.add_trace(go.Scatter(
                        x=overbound["datetime"].to_list(),
                        y=overbound["high"].to_list(),
                        name="Over bought",
                        mode="markers",
                        marker=dict(size=5)
                    )           
                )
        fig.add_trace(go.Scatter(
                        x=underbound["datetime"].to_list(),
                        y=underbound["low"].to_list(),
                        name="Over sell",
                        mode="markers",
                        marker=dict(size=5)
                    )           
                )
        fig.update_layout(
                        title={
                            "text": self.title,
                            "xanchor": "center",
                            "x": 0.5
                        },
                        font=dict(size=18)
                )
        return fig

    def __columns_exist(self, df: pl.DataFrame) -> bool:
        for col in df.columns:
            if "Sig" in col:
                self.signal = col
            elif col.startswith("SMA"):
                self.moving_avg = col
            elif col.startswith("Upper"):
                self.upper_band = col
            elif col.startswith("Lower"):
                self.lower_band = col

        if self.moving_avg == "" or \
            self.upper_band == "" or \
            self.lower_band == "" or \
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