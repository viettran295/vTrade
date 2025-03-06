from strategy import Strategy
import polars as pl
from loguru import logger
from typing import List
import time
import asyncio
from strategy.vtrade import vTrade

class SignalScanner:
    def __init__(self, strategy: Strategy, stocks_list: List[str], day_to_scan: int = 7) -> None:
        self.strategy = strategy
        self.stocks_list = stocks_list
        self.day_to_scan = day_to_scan
        self.short_MA = 20
        self.long_MA = 50
        self.signals = {
            s: {
                "buy": pl.DataFrame,
                "sell": pl.DataFrame
            }
            for s in self.stocks_list
        }
        self.last_query_time = {}
        self.cache = {}
        self.query_interval = 3600

    def set_stocks_to_scan(self, stocks_list: List[str]):
        for s in stocks_list:
            self.stocks_list.append(s)
    
    def set_short_long_MA(self, short_MA: str, long_MA: str):
        if "SMA" in short_MA and "SMA" in long_MA:
            self.short_MA = short_MA
            self.long_MA = long_MA
        elif "EWM" in short_MA and "EWM" in long_MA:
            self.short_MA = short_MA
            self.long_MA = long_MA
        else:
            logger.error("Invalid moving average type")
    
    async def scan_async(self, sig_types: List[str]):
        curr_time = time.time()
        vtr = vTrade()
        stocks_to_fetch = []
        for stock in self.stocks_list:
            if curr_time - self.last_query_time.get(stock, 0) > self.query_interval:
                stocks_to_fetch.append(stock)

        logger.info(" --- Async scanner is starting  ---")
        fetched_data = await vtr.get_stocks_async(stocks_to_fetch)

        for stock, fetched_df in fetched_data.items():
            self.cache[stock] = fetched_df 
            self.last_query_time[stock] = curr_time

        tasks = []
        for stock in self.stocks_list:
            for sig_type in sig_types:
                df = self.cache.get(stock, None)
                if df is not None:
                    tasks.append(self.__process_stock_data(stock, df, sig_type))
                    logger.debug(f"Executing processing task for {stock} - {sig_type}")
                else:
                    logger.error(f"Invalid Dataframe while getting from cache {stock} - {sig_type}")
        await asyncio.gather(*tasks)
        self.__show_signals()

    def scan(self, sig_types: List[str]):
        asyncio.run(self.scan_async(sig_types))

    def scan_MA(self, df: pl.DataFrame) -> pl.DataFrame:
        return self.strategy.execute(df, self.short_MA, self.long_MA)
    
    def scan_RSI(self, df: pl.DataFrame) -> pl.DataFrame:
        pass
        # return self.calc_RSI(df)

    def scan_bollinger_bands(self, df: pl.DataFrame) -> pl.DataFrame:
        pass
        # return self.calc_bollinger_bands(df)

    def __signal_regconize(self, df: pl.DataFrame):
        if df is None:
            return
        
        buy_signals = {
            "datetime": [],
            "close": [],
        }
        sell_signals = buy_signals
        init = False

        for sig in df.tail(self.day_to_scan).iter_rows(named=True):
            if not init:
                signal_key = list(sig.keys())[-1]
                buy_signals[signal_key] = []
                sell_signals[signal_key] = []
                init = True

            if sig[signal_key] == self.strategy.bin_signal["buy"]:
                buy_signals["datetime"].append(sig["datetime"])
                buy_signals["close"].append(sig["close"])
                buy_signals[signal_key].append(sig[signal_key])
            if sig[signal_key] == self.strategy.bin_signal["sell"]:
                sell_signals["datetime"].append(sig["datetime"])
                sell_signals["close"].append(sig["close"])
                sell_signals[signal_key].append(sig[signal_key])
                
        logger.info("Recognized sell-buy signal")

        return buy_signals, sell_signals
    
    def __show_signals(self):
        logger.warning("============ Sell-buy signals ============")
        for stock in self.stocks_list:
            if not self.signals[stock]["buy"].is_empty():
                logger.info(f"{stock} buy signals: {self.signals[stock]['buy']}")
            elif not self.signals[stock]["sell"].is_empty():
                logger.info(f"{stock} sell signals: {self.signals[stock]['sell']}")
        logger.warning("========================================== \n")
    
    async def __process_stock_data(self, stock, df, sig_type):
        if df is not None:
            match sig_type:
                case "RSI":
                    df = self.scan_RSI(df)
                case "BB":
                    df = self.scan_bollinger_bands(df)
                case "MA":
                    df = self.scan_MA(df)

            if df is not None and self.strategy.signal in df.columns:
                buy_sig, sell_sig = self.__signal_regconize(df)
                self.signals[stock]["buy"] = pl.DataFrame(buy_sig)
                self.signals[stock]["sell"] = pl.DataFrame(sell_sig)