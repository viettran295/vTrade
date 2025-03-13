from signal_scanner import SignalScanner
from utils import log_exectime
from strategy import StrategyCrossingMA, StrategyRSI, StrategyBollingerBands

stocks = ["MARA", "AAPL", "COIN", "CNSWF", "AMZN", "GOOGL", "PLTR", "SPOT"]
sig_types = ["MA", "RSI", "BB"]

x_ma = StrategyCrossingMA()
rsi = StrategyRSI()
bb = StrategyBollingerBands()

strategies = [x_ma, rsi, bb]
ss = SignalScanner(strategy=strategies, stocks_list=stocks)

@log_exectime
def main():
    ss.scan()
            
if __name__ == "__main__":
    main()
