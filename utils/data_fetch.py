from dotenv import load_dotenv
load_dotenv()
import os
from datetime import date, timedelta, datetime
import polars as pl 
from loguru import logger
import asyncio
import aiohttp
import websockets
import json
from typing import List


class DataFetch():
    url = f"https://api.twelvedata.com"

    def __init__(self) -> None:
        self.end_date = date.today() - timedelta(days=1)
        self.start_date = self.end_date - timedelta(days=365*3)
        self.api_key = os.getenv("12_DATA_KEY")
        self.coincap_key = os.getenv("COINCAP_KEY")
    
    async def get_stocks_async(self, stock) -> dict:
        async with aiohttp.ClientSession() as session:
            return await self.fetch_data(session, stock) 
    
    async def get_batch_stocks_async(self, stocks: List[str]) -> dict:
        async with aiohttp.ClientSession() as session:
            return await self.fetch_data(session, stocks, fetch_batch=True)
    
    async def fetch_data(
            self, 
            session: aiohttp.ClientSession, 
            symbols: List[str], 
            interval="1day", 
            start_date=None, 
            end_date=None,
            fetch_batch: bool=False
    ):
        start_date = start_date or self.start_date
        end_date = end_date or self.end_date
        
        if fetch_batch:
            return await self.__fetch_batch_data(session, symbols, interval, start_date, end_date)
        else:
            return await self.__fetch_stock_data(session, symbols[0], interval, start_date, end_date)

    async def __fetch_batch_data(
            self, 
            session: aiohttp.ClientSession, 
            symbols: List[str], 
            interval="1day", 
            start_date=None, 
            end_date=None
    ) -> dict:
        
        self.url += "/batch"
        batch_req = {}
        for symbol in symbols:
            batch_req[symbol] = {
                "url": 
                    f"/time_series?symbol={symbol}&interval={interval}&start_date={start_date}&end_date={end_date}&apikey={self.api_key}"
            }
        try:
            async with session.post(self.url, data=json.dumps(batch_req), timeout=5) as resp:
                data = await resp.json()
                logger.debug(f"Received response when batch fetch {symbols} data")
        except TimeoutError as e :
            logger.error(f"Timeout when batch request {symbols} -> {e}")
            return symbols, None
        except ConnectionError as e:
            logger.error(f"Connection error when batch request {symbols} -> {e}")
            return symbols, None
        except Exception as e:
            logger.error(f"Error when batch request {symbols} -> {e}")
        
        return self.__process_batch_data(data["data"])

    async def __fetch_stock_data(
            self, 
            session: aiohttp.ClientSession, 
            symbol: str,
            interval: str="1day", 
            start_date=None, 
            end_date=None
    ) -> dict:
        
        self.url += f"/time_series?symbol={symbol}&interval={interval}&start_date={start_date}&end_date={end_date}&apikey={self.api_key}"
        try:
            async with session.get(self.url, timeout=5) as resp:
                resp.raise_for_status()
                data = await resp.json()
                result = {
                    symbol: self.__process_single_data(data)
                }
                logger.debug(f"Received response when fetch {symbol} data")
        except TimeoutError as e :
            logger.error(f"Timeout when request {symbol} -> {e}")
            return None
        except ConnectionError as e:
            logger.error(f"Connection error when reques {symbol} -> {e}")
            return None
        except Exception as e:
            logger.error(f"Error when request {symbol} -> {e}")
            return None
        return result
    
    async def connect_websocket(self, asset: str="bitcoin"):
        uri = f"wss://ws.coincap.io/prices?assets={asset}"

        async with websockets.connect(uri) as ws:
            logger.debug("Connecting to websockets...")
            try:
                while True:
                    mess = await ws.recv()
                    data = json.loads(mess)
                    if data:
                        price = data[f"{asset}"]
                        timestamp = datetime.now()
                        logger.info(f"Timestamp: {timestamp} - Price: {price}")
                    await self.__close_websocket(ws, 1)

            except websockets.exceptions.ConnectionClosedOK:
                logger.debug("WebSocket connection closed gracefully.")
            except Exception as e:
                logger.error(f"WebSocket error: {e}") 
            
    @staticmethod
    async def __close_websocket(socket, after_mins: int=5):
        try:
            await asyncio.sleep(60 * after_mins)
            await socket.close()
            logger.debug(f"Socket closed after {after_mins} minutes.")
        except OSError as e:
            logger.error(f"Error closing socket: {e}")

    @staticmethod
    def __process_single_data(data: dict) -> pl.DataFrame:
        if "values" in data:
            df = pl.DataFrame(data['values'])
            df = df.with_columns(
                pl.col(df.columns[0]).str.strptime(pl.Datetime).cast(pl.Date),
                *[pl.col(i).cast(pl.Float64) for i in df.columns[1:]], # Unpack list
            )
            df = df.sort(by=pl.col("datetime"), descending=False)
            return df
        else:
            return None
        
    @staticmethod
    def __process_batch_data(data: dict) -> dict:
        results = {}
        for req_key, req_val in data.items():
            if req_val["status"] != "success" and "response" not in req_val:
                continue
            repsponse = req_val["response"]
            if "values" not in repsponse:
                continue

            df = pl.DataFrame(repsponse['values'])
            df = df.with_columns(
                pl.col(df.columns[0]).str.strptime(pl.Datetime).cast(pl.Date),
                *[pl.col(i).cast(pl.Float64) for i in df.columns[1:]], # Unpack list
            )
            df = df.sort(by=pl.col("datetime"), descending=False)
            results[req_key] = df
        return results
    
if __name__ == "__main__":
    vtr = vTrade()
    asyncio.run(vtr.connect_websocket())