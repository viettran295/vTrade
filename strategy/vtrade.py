from dotenv import load_dotenv
load_dotenv()
import os
from datetime import date, timedelta
import polars as pl 
from loguru import logger
import asyncio
import aiohttp
from typing import Tuple, List

class vTrade():
    def __init__(self) -> None:
        self.end_date = date.today() - timedelta(days=1)
        self.start_date = self.end_date - timedelta(days=365*3)
        self.api_key = os.getenv("12_DATA_KEY")
    
    async def get_stocks_async(self, stocks: List[str]) -> dict:
        results = {} 
        async with aiohttp.ClientSession() as session:
            tasks = [self.__fetch_stock_data(session, stock) \
                    if stock is not None else stock \
                    for stock in stocks]
            logger.debug(f"Fetching {stocks} data")
            for symbol, df in await asyncio.gather(*tasks):
                results[symbol] = df
        return results

    async def __fetch_stock_data(self, session, symbol, interval="1day", start_date=None, end_date=None) -> Tuple[str, pl.DataFrame]:
        if end_date is None:
            end_date = self.end_date
        if start_date is None:
            start_date = self.start_date
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&start_date={start_date}&end_date={end_date}&apikey={self.api_key}"
        
        try:
            async with session.get(url, timeout=5) as resp:
                resp.raise_for_status()
                data = await resp.json()
                logger.debug(f"Received response when fetch {symbol} data")
        except TimeoutError as e :
            logger.error(f"Timeout when request {symbol} -> {e}")
            return symbol, None
        except ConnectionError as e:
            logger.error(f"Connection error when reques {symbol} -> {e}")
            return symbol, None
        except Exception as e:
            logger.error(f"Error when request {symbol} -> {e}")
        
        # Add data to DataFrame
        if "values" in data:
            df = pl.DataFrame(data['values'])
            df = df.with_columns(
                pl.col(df.columns[0]).str.strptime(pl.Datetime).cast(pl.Date),
                *[pl.col(i).cast(pl.Float64) for i in df.columns[1:]], # Unpack list
            )
            df = df.sort(by=pl.col("datetime"), descending=False)
            return symbol, df
        else:
            return symbol, None