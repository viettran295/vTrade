from signal_scanner import SignalScanner
from utils import log_exectime
from strategy.crossing_ma import CrossingMA

stocks = ["MARA", "MSTR", "AAPL", "COIN", "CNSWF", "AMZN", "NVDA", "GOOGL"]
sig_types = ["MA", "RSI", "BB"]

x_ma = CrossingMA()

ss = SignalScanner(strategy=x_ma, stocks_list=stocks)

@log_exectime
def main():
    ss.scan(sig_types=sig_types)
            
if __name__ == "__main__":
    main()
