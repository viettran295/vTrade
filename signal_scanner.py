from strategy import Strategy
import polars as pl
from loguru import logger
from typing import List
import time
from vtrade import vTrade

class SignalScanner(Strategy):
    def __init__(self, stocks_list: List[str], day_to_scan: int = 7) -> None:
        super().__init__()
        self.stocks_list = stocks_list
        self.day_to_scan = day_to_scan
        self.short_MA = "SMA_20"
        self.long_MA = "SMA_100"
        self.signals = {
            s: {
                "buy": None,
                "sell": None
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
    
    def scan(self, sig_type: str):
        curr_time = time.time()
        vtr = vTrade()
        for stock in self.stocks_list:
            logger.info(f" --- Scanning {stock} for {sig_type} ---")
            if curr_time - self.last_query_time.get(stock, 0) > self.query_interval:
                df = vtr.get_stock_data(stock)
                self.cache[stock] = df 
                self.last_query_time[stock] = curr_time
            else:
                df = self.cache[stock]

            if df is not None:
                match sig_type:
                    case "RSI":
                        df = self.scan_RSI(df)
                    case "BB":
                        df = self.scan_bollinger_bands(df)
                    case "MA":
                        df = self.scan_MA(df)

                if df is not None and self.sell_buy_sig in df.columns:
                    buy_sig, sell_sig = self.__signal_regconize(df)
                    self.signals[stock]["buy"] = buy_sig
                    self.signals[stock]["sell"] = sell_sig
            else:
                logger.error(f"Invalid Dataframe while scanning {stock}")
        self.__show_signals()

    def scan_MA(self, df: pl.DataFrame) -> pl.DataFrame:
        df = self.calc_MA(df, self.short_MA)
        df = self.calc_MA(df, self.long_MA)
        return self.calc_crossing_MA(df, self.short_MA, self.long_MA)
    
    def scan_RSI(self, df: pl.DataFrame) -> pl.DataFrame:
        return self.calc_RSI(df)

    def scan_bollinger_bands(self, df: pl.DataFrame) -> pl.DataFrame:
        return self.calc_bollinger_bands(df)

    def __signal_regconize(self, df: pl.DataFrame):
        if df is None:
            return
        
        buy_signals = []
        sell_signals = []

        for sig in df.tail(self.day_to_scan).iter_rows(named=True):
            if sig[self.sell_buy_sig] == self.signal["buy"]:
                buy_signals.append((sig["datetime"], sig["close"], sig["Signal"]))
            if sig[self.sell_buy_sig] == self.signal["sell"]:
                sell_signals.append((sig["datetime"], sig["close"], sig["Signal"]))
        logger.info("Recognized sell-buy signal")
        return buy_signals, sell_signals
    
    def __show_signals(self):
        logger.warning("============ Sell-buy signals ============")
        for stock in self.stocks_list:
            if self.signals[stock]["buy"]:
                logger.info(f"{stock} buy signals: {self.signals[stock]['buy']}")
            elif self.signals[stock]["sell"]:
                logger.info(f"{stock} sell signals: {self.signals[stock]['sell']}")
        logger.warning("========================================== \n")