from signal_scanner import SignalScanner
from utils import log_exectime

stocks = ["MARA", "MSTR", "AAPL", "COIN", "CNSWF", "AMZN", "NVDA", "GOOGL"]
sig_types = ["MA", "RSI", "BB"]

ss = SignalScanner(stocks)

@log_exectime
def main():
    ss.scan(sig_types=sig_types)
            
if __name__ == "__main__":
    main()
