from strategy import Strategy
import polars as pl
from loguru import logger
from typing import List

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
        
    def scan_MA(self):
        for stock in self.stocks_list:
            df = self.get_stock_data(stock)
            df = self.calc_MA(df, self.short_MA)
            df = self.calc_MA(df, self.long_MA)
            df_ma = self.calc_crossing_MA(df, self.short_MA, self.long_MA)
            if df_ma is not None and self.sell_buy_sig in df_ma:
                buy_sig, sell_sig = self.__signal_regconize(df_ma)
                self.signals[stock]["buy"] = buy_sig
                self.signals[stock]["sell"] = sell_sig
        logger.warning("Finish scanning MA signals")
        self.__show_signals()
    
    def scan_RSI(self):
        for stock in self.stocks_list:
            df = self.get_stock_data(stock)
            df = self.calc_RSI(df)
            if df is not None and self.sell_buy_sig in df:
                buy_sig, sell_sig = self.__signal_regconize(df)
                self.signals[stock]["buy"] = buy_sig
                self.signals[stock]["sell"] = sell_sig
        logger.warning("Finish scanning RSI signals")
        self.__show_signals()

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
            else:
                logger.info(f"There is no sell-buy signal for {stock}")
        logger.warning("========================================== \n")