from dotenv import load_dotenv
load_dotenv()
import os
import requests
from datetime import date, timedelta
import polars as pl 
import plotly.graph_objects as go

class vTrade():

    fig = go.Figure()
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
    MA_types = ["SMA", "EWM"]

    def __init__(self) -> None:
        self.end_date = date.today() - timedelta(days=1)
        self.start_date = self.end_date - timedelta(days=365*3)
        self.api_key = os.getenv("12_DATA_KEY")
        self.columns = ["open", "close", "high", "close"]
    
    def get_stock_data(self, symbol, interval="1day", start_date=None, end_date=None) -> pl.DataFrame:
        if end_date is None:
            end_date = self.end_date
        if start_date is None:
            start_date = end_date - timedelta(days=365*3)
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&start_date={start_date}&end_date={end_date}&apikey={self.api_key}"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        # Add data to DataFrame
        if data["values"]:
            df = pl.DataFrame(data['values'])
            df = df.with_columns(
                pl.col(df.columns[0]).str.strptime(pl.Datetime).cast(pl.Date),
                *[pl.col(i).cast(pl.Float64) for i in df.columns[1:]], # Unpack list
            )
            df = df.sort(by=pl.col("datetime"), descending=False)
            return df
        else:
            return None

    def calc_MA(self, symbol, MA1, MA2, MA_type="SMA", df=None) -> pl.DataFrame:
        if df is None:
            df = self.get_stock_data(symbol)
        
        if isinstance(MA_type, str):
            # Convert string to list
            MA_type = [MA_type]

        for ma_type in MA_type:
            if ma_type == "SMA":
                df = df.with_columns(
                    pl.col("high").rolling_mean(window_size=MA1).alias(f"SMA_{MA1}"),
                    pl.col("high").rolling_mean(window_size=MA2).alias(f"SMA_{MA2}")
                )
            if ma_type == "EWM":
            # Exponentially weighted moving average
                df = df.with_columns(
                    pl.col("high").ewm_mean(span=MA1).alias(f"EWM_{MA1}"),
                    pl.col("high").ewm_mean(span=MA2).alias(f"EWM_{MA2}")
                )
        return df
    
    @staticmethod
    def _check_listSubstr_in_Str(substr_ls: list[str], str_ls: list[str]) -> bool:
        for substr in substr_ls:
            for string in str_ls:
                if substr in string:
                    return True
        return False

    @staticmethod
    def _get_fullname_cols(type_names: list[str], col_names: list[str]) -> list[str]:
        """
        e.g return detail name like EWM_20 from columns of dataframe 
        """
        res_cols = []
        for type_name in type_names:
            for col in col_names:
                if type_name in col:
                    res_cols.append(col)
        return res_cols


    def show_MA(self, df: pl.DataFrame):
        if not vTrade._check_listSubstr_in_Str(self.columns, df.columns): 
            return
        
        visualize_cols = self._get_fullname_cols(self.MA_types, df.columns)
        
        if len(visualize_cols) <= 0:
            return
        
        self.fig.add_trace(go.Bar(x=df["datetime"], y=df["high"]))

        for ma_type in visualize_cols:
            self.fig.add_trace(go.Line(x=df["datetime"],
                                    y=df[f"{ma_type}"],
                                    name=f"{ma_type}"))
            
        self.fig.update_layout(title={"text": "Stock price",
                                "xanchor": "center",
                                "x": 0.5},
                          xaxis=dict(title="Date"),
                          yaxis=dict(title="$ USD"))
        self.fig.show()