from signal_scanner import SignalScanner
from utils import log_exectime
from strategy.crossing_ma import StrategyCrossingMA
from strategy.rsi import StrategyRSI

stocks = ["MARA", "MSTR", "AAPL", "COIN", "CNSWF", "AMZN", "NVDA", "GOOGL"]
sig_types = ["MA", "RSI", "BB"]

x_ma = StrategyCrossingMA()
rsi = StrategyRSI()
strategies = [x_ma, rsi]
ss = SignalScanner(strategy=strategies, stocks_list=stocks)

@log_exectime
def main():
    ss.scan()
            
if __name__ == "__main__":
    main()
